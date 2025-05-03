# backend\app\routes\call_agent\apis.py

import json
import base64
import asyncio
import websockets
from config import CONFIG
from typing import Optional
from datetime import datetime
from app.utils.logging.logger import LOG
from app.routes.call_agent.prompts import Prompts
from app.utils.err.error import InternalServerError
from websockets.asyncio.client import ClientConnection
from fastapi.responses import HTMLResponse, JSONResponse
from app.routes.call_agent.dtos import CallMetadata, CallClassification
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Query
from app.routes.call_agent.helper import (
    call_openai_api,
    extract_voice_name,
    close_after_timeout,
    internet_search_func,
    user_message_to_openai,
    initial_settings_openai,
    append_prompt_scenarios,
    close_websocket_connections,
    fetch_and_validate_mock_response,
    insert_call_metadata_into_database,
)    

# Constants
tag: str = "WebSocket Twilio APIs"
websocket_twilio_apis_router: APIRouter = APIRouter(tags=[tag], prefix="/twilio")

OPENAI_URL = f"wss://api.openai.com/v1/realtime?model={CONFIG.openai_realtime_model}"
HEADERS = {
    "Authorization": f"Bearer {CONFIG.openai_api_key}",
    "OpenAI-Beta": "realtime=v1"
}

LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'session.created'
]
SHOW_TIMING_MATH = False

# Twilio APIs
@websocket_twilio_apis_router.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    LOG.info("Handling incoming Twilio call")
    
    # Extract form data from request
    form_data = await request.form()
    
    # Extract call information
    caller_number = form_data.get('From', 'Unknown')
    twilio_number = form_data.get('To', 'Unknown')
    call_sid = form_data.get('CallSid', 'Unknown')
    
    # Log the call information
    LOG.info(f"📞 Incoming call from: {caller_number}")
    LOG.info(f"📲 Call is being received on: {twilio_number}")
    LOG.info(f"📱 Call SID: {call_sid}")
    
    # Store phone numbers in app state
    request.app.state.call_data[call_sid] = {
        'caller_number': caller_number,
        'twilio_number': twilio_number
    }
    # LOG.info(f"Stored phone numbers in app state for SID: {call_sid}")
    
    response = VoiceResponse()
    # response.say("Hello! Thank you for calling Silverline. Please hold while we connect you.")
    host = request.url.hostname
    # LOG.debug(f"Using host for WebSocket connection: {host}")
    connect = Connect()
    
    # Pass the CallSid as a custom parameter to the stream
    custom_params = {'CallSid': call_sid}
    connect.stream(url=f'wss://{host}/ai/twilio/media-stream', parameter_name='customParameters', parameter_value=json.dumps(custom_params))
    
    response.append(connect)
    LOG.info("Returning TwiML response for incoming call")
    return HTMLResponse(content=str(response), media_type="application/xml")

# WebSocket Route
@websocket_twilio_apis_router.websocket("/media-stream")
async def openai_websocket_session(
    websocket: WebSocket,
):
    """
    Establish a WebSocket connection that proxies messages between
    the client and the OpenAI Realtime API, with a forced session
    timeout specified in the fetched JSON.
    """
    openai_ws: Optional[ClientConnection] = None

    # Call metadata tracking
    call_start_time = datetime.now()
    call_metadata = CallMetadata(
        datetime=call_start_time,
        caller_id=None,
        caller_number=None,
        twilio_number=None,
        call_duration=None,
        call_transcript=""
    )
    user_queries = []
    ai_responses = []

    try:
        LOG.info("Client requested WebSocket connection")
        await websocket.accept()
        LOG.info("WebSocket connection accepted")

        # Fetch and validate mock response from backend
        LOG.info("Fetching and validating mock response from backend")
        response_from_backend = await fetch_and_validate_mock_response(agent_id="default_agent")
        if not response_from_backend:
            await close_websocket_connections(
                "No valid backend JSON; closing connections.",
                openai_ws,
                websocket
            )
            return
        # LOG.info("Response from backend:")
        # LOG.info(response_from_backend)
        
        # Connect to OpenAI WebSocket
        try:
            openai_ws = await websockets.connect(uri=OPENAI_URL, additional_headers=HEADERS)
            LOG.info("Connected to OpenAI WebSocket")
        except Exception as exc:
            LOG.error(f"Error connecting to OpenAI: {exc}", exc_info=True)
            await close_websocket_connections(
                "OpenAI WS connection error.",
                openai_ws,
                websocket
            )
            return

        # Create timeout task based on session timeout from JSON
        session_timeout_seconds = response_from_backend["sessionTimeoutInSeconds"]
        timeout_task = asyncio.create_task(
            close_after_timeout(session_timeout_seconds, openai_ws, websocket)
        )
        LOG.info(f"Created session timeout task for {session_timeout_seconds} seconds.")

        # Append scenario prompts and gather ending messages
        response_from_backend, ending_messages_for_regex = \
            await append_prompt_scenarios(response_from_backend)

        # Set the voice model name
        voice_model_name = response_from_backend.get("voiceModelName", "alloy")
        voice_model_name_cleaned = await extract_voice_name(voice_model_name)
        LOG.info(f"Voice model name set to: {voice_model_name_cleaned}")

        # Send the final instructions (prompt) to OpenAI
        try:
            prompt = response_from_backend.get("instructions", "")
            await initial_settings_openai(openai_ws, prompt, voice_model_name_cleaned)
            LOG.info("Sent initial settings to OpenAI")
        except Exception as exc:
            LOG.error(f"Error connecting to OpenAI: {exc}", exc_info=True)
            await close_websocket_connections(
                "OpenAI WS connection error.",
                openai_ws,
                websocket
            )
            return

        # Handle conversation initiation based on configuration
        initiation_mode = response_from_backend.get("initiationMode", "AI Initiates (Dynamic Message)")
        if initiation_mode == "AI Initiates (Defined Message)":
            LOG.info("Initiation mode: AI Initiates (Defined Message)")
            await user_message_to_openai(openai_ws, "Hello!")
            LOG.info("Sent initial user message to OpenAI: 'Hello!'")
            defined_message = response_from_backend.get("aiDefinedMessage", "Hello!")
            LOG.info(f"AI will start with a defined initial message: '{defined_message}'")
        elif initiation_mode == "AI Initiates (Dynamic Message)":
            LOG.info("Initiation mode: AI Initiates (Dynamic Message)")
            await user_message_to_openai(openai_ws, "Hello!")
            LOG.info("Sent initial user message: 'Hello!'")
            LOG.info("AI will start with dynamic initial message")
        else:
            LOG.info("Initiation mode: User Initiates")
            LOG.info("User will initiate the conversation; no initial message sent.")

        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None

        async def receive_from_client():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.state.name == 'OPEN':
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        
                        # Extract call metadata if available
                        if 'start' in data and 'callSid' in data['start']:
                            call_sid = data['start'].get('callSid')
                            call_metadata.caller_id = call_sid
                            
                            # Retrieve phone numbers from app state
                            call_sid_from_params = data['start'].get('customParameters', {}).get('CallSid')
                            if call_sid_from_params and call_sid_from_params in websocket.app.state.call_data:
                                # LOG.info(f"Retrieved phone numbers for call SID: {call_sid_from_params}")
                                call_metadata.caller_number = websocket.app.state.call_data[call_sid_from_params]['caller_number']
                                call_metadata.twilio_number = websocket.app.state.call_data[call_sid_from_params]['twilio_number']
                            elif call_sid in websocket.app.state.call_data:
                                # LOG.info(f"Retrieved phone numbers for call SID: {call_sid}")
                                call_metadata.caller_number = websocket.app.state.call_data[call_sid]['caller_number']
                                call_metadata.twilio_number = websocket.app.state.call_data[call_sid]['twilio_number']
                        
                        # LOG.info(f"Incoming Twilio stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                LOG.info("Client disconnected (receive_from_client)")
            except websockets.exceptions.ConnectionClosedOK as e:
                LOG.info(f"WebSocket connection closed gracefully: {e}")
            except websockets.exceptions.ConnectionClosedError as e:
                LOG.warning(f"WebSocket connection closed with error: {e}")
            except Exception as e:
                LOG.error(f"Unexpected error in receive_from_client: {e}", exc_info=True)
            finally:
                LOG.info("Exiting receive_from_client")

        async def receive_from_openai():
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)

                    if response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                LOG.debug(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                        # Update last_assistant_item
                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    # Handle speech interruption
                    if response.get('type') == 'input_audio_buffer.speech_started':
                        LOG.info("Speech started from client detected.")
                        if last_assistant_item:
                            await handle_speech_started_event()

                    # Handle audio transcription
                    if response.get("type") == "conversation.item.input_audio_transcription.completed":
                        user_query = response.get("transcript", "")
                        LOG.info(f"User query (audio): {user_query}")
                        user_queries.append(user_query)  # Store for transcript

                    # Handle text input
                    elif response.get("type") == "conversation.item.created":
                        item = response.get("item", {})
                        content = item.get("content", [])
                        if content and content[0]:
                            if content[0].get("type") == "input_text":
                                user_query = content[0].get("text", "")
                                LOG.info(f"User query (text): {user_query}")
                                user_queries.append(user_query)  # Store for transcript

                    # Handle response completion
                    elif response.get("type") == "response.done":
                        resp_data = response.get("response", {})
                        if resp_data.get("output"):
                            output = resp_data["output"]
                            if output and "content" in output[0]:
                                transcript = output[0]["content"][0].get("transcript", "")
                                LOG.info(f"OpenAI response: {transcript}")
                                ai_responses.append(transcript)  # Store for transcript

                                # Check for end-call trigger phrases
                                if transcript.lower() in ending_messages_for_regex:
                                    # Capture final call metadata before closing
                                    await capture_call_metadata()
                                    await close_websocket_connections(
                                        "Ending WebSocket session due to regex match",
                                        openai_ws,
                                        websocket
                                    )
                                    return

                        # Check for rate limit exceeded
                        if resp_data.get("status") == "failed":
                            error_details = resp_data.get("status_details", {}).get("error", {})
                            if error_details.get("type") == "requests":
                                code = error_details.get("code", "")
                                error_message = error_details.get("message", "")
                                LOG.error(f"OpenAI error: code={code}, msg={error_message}")

                                if code == "rate_limit_exceeded":
                                    wait_time = "unknown time"
                                    if "Try again in" in error_message:
                                        try:
                                            wait_time = error_message.split("Try again in ")[1].split(".")[0]
                                        except IndexError:
                                            pass
                                    LOG.error(
                                        f"Rate limit exceeded: {error_message}. "
                                        f"Please try again in {wait_time}."
                                    )
                                    await websocket.send_text(
                                        f"Error: Rate limit exceeded. Please try again in {wait_time}."
                                    )

                                await close_websocket_connections(
                                    f"OpenAI responded with {code}, closing.",
                                    openai_ws,
                                    websocket
                                )
                                return

                        # Check for other errors
                        response_details = response.get("response", {})
                        status = response_details.get("status", "unknown")

                        if status == "failed":
                            status_details = response_details.get("status_details", {})
                            error_details = status_details.get("error", {})
                            error_type = error_details.get("type", "Unknown error type")
                            error_code = error_details.get("code", "Unknown code")
                            error_message = error_details.get("message", "No error message provided")
                            event_id = response.get("event_id", "No event ID provided")

                            LOG.error(
                                f"Response failed. Event ID: {event_id}, "
                                f"Error Type: {error_type}, "
                                f"Error Code: {error_code}, "
                                f"Message: {error_message}"
                            )

                            await close_websocket_connections(
                                f"OpenAI responded with {error_code}, closing.",
                                openai_ws,
                                websocket
                            )
                            return

                    # Handle error events
                    elif response.get("type") == "error":
                        error_details = response.get("error", {})
                        error_type = error_details.get("type", "Unknown error type")
                        error_code = error_details.get("code", "Unknown code")
                        error_message = error_details.get("message", "No error message provided")
                        event_id = error_details.get("event_id", "No event ID provided")

                        LOG.error(
                            f"Error Type: {error_type}, "
                            f"Error Code: {error_code}, "
                            f"Message: {error_message}, "
                            f"Event ID: {event_id}"
                        )

                        await close_websocket_connections(
                            f"OpenAI responded with {error_code}, closing.",
                            openai_ws,
                            websocket
                        )
                        return

                    # Handle tool/function calls
                    elif (
                        response.get("type") == "response.function_call_arguments.done"
                        and response.get("name") == "internet_search"
                    ):
                        # Log the detection of the internet search tool/function call
                        LOG.info("Internet search tool/function call detected")

                        # Extract the language from the response
                        lang = response_from_backend.get("language", "en-US")
                        
                        # Extract the call ID from the response
                        call_id = response.get("call_id", "No call ID provided")
                        
                        # Call the internet search tool function
                        LOG.info("Now calling internet search tool funciton")
                        await internet_search_func(openai_ws, lang, user_query, call_id)
                        
                        LOG.info("Letting OpenAI speak with the function call output")
                        payload = {
                            "type": "response.create"
                        }
                        await openai_ws.send(json.dumps(payload))
                        

                    # Forward everything else to the client
                    await websocket.send_text(openai_message)

            except Exception as exc:
                LOG.error(f"Error receiving from OpenAI: {exc}", exc_info=True)

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    pass

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        pass
                    
                    # Instead of trying to calculate exact truncation points which can lead to errors,
                    # we'll just skip the truncation entirely and clear the audio stream
                    # This is a more reliable approach than trying to guess the correct audio length
                    LOG.info("User interrupted assistant. Clearing audio without truncation.")
                    
                    # Skip the truncation completely - just clear the audio
                    # The previous approach led to "audio content is already shorter than X" errors
                    # even with conservative estimates

                # Always clear the stream when speech is detected
                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None
            else:
                pass

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"}
                }
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')
            else:
                pass

        async def capture_call_metadata():
            """Capture final call metadata and return as JSON"""
            LOG.info("Capturing call metadata")
            # Calculate call duration
            call_end_time = datetime.now()
            duration_seconds = int((call_end_time - call_start_time).total_seconds())
            call_metadata.call_duration = duration_seconds
            
            # Combine user queries and AI responses into a transcript
            transcript_parts = []
            for i in range(max(len(user_queries), len(ai_responses))):
                if i < len(user_queries):
                    transcript_parts.append(f"User: {user_queries[i]}")
                if i < len(ai_responses):
                    transcript_parts.append(f"AI: {ai_responses[i]}")
            transcript_content = "\n".join(transcript_parts)
            
            # Classify the call
            LOG.info("Starting call classification wiht gpt")
            classification_prompt = Prompts.classify_call_prompt.format(call_transcript=transcript_content)
            
            # Get call classification using OpenAI
            try:
                classification_response, token_usage = await call_openai_api(
                    prompt=classification_prompt,
                    validation_schema=CallClassification,
                    model=CONFIG.classifier_model
                )
                classification_response_json = json.loads(classification_response)
                validated_classification = CallClassification(**classification_response_json)
            except Exception as e:
                LOG.error(f"Classification failed: {e}")
                raise
            
            LOG.info("Adding classification to metadata")
            call_metadata.is_spam = validated_classification.is_spam.value
            call_metadata.reason = validated_classification.reason
            call_metadata.type = validated_classification.type.value

            # Clean up call data from app state
            if call_metadata.caller_id and call_metadata.caller_id in websocket.app.state.call_data:
                LOG.info(f"Cleaning up call data for SID: {call_metadata.caller_id}")
                websocket.app.state.call_data.pop(call_metadata.caller_id, None)

            # Convert the metadata to a dict and ensure datetime is serialized as string
            metadata_dict = call_metadata.model_dump()

            # Convert datetime to ISO format string
            # LOG.info("Converting datetime to ISO format string")
            metadata_dict["datetime"] = call_metadata.datetime.isoformat()
            # LOG.info("Datetime converted to ISO format string")
            # LOG.info(f"Converted datetime: {metadata_dict['datetime']}")

            # Log the call metadata
            # LOG.info(f"Call completed. Final Metadata: {metadata_dict}")
            
            return metadata_dict

        # Launch tasks concurrently
        client_task = asyncio.create_task(receive_from_client())
        openai_task = asyncio.create_task(receive_from_openai())

        # Wait for first task to complete
        done, pending = await asyncio.wait(
            [client_task, openai_task, timeout_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel any tasks still pending
        for task in pending:
            task.cancel()

    except Exception as exc:
        LOG.error(f"Error in WebSocket session: {exc}", exc_info=True)
        raise InternalServerError()

    finally:
        # Capture call metadata before closing connections
        try:
            call_metadata_from_route = await capture_call_metadata()
            await insert_call_metadata_into_database(call_metadata_from_route)
        except Exception as e:
            LOG.error(f"Error capturing call metadata: {e}", exc_info=True)
            
        # Ensure connections are closed in all cases
        await close_websocket_connections(
            "Cleaning up WebSocket connections in finally block",
            openai_ws,
            websocket
        )
