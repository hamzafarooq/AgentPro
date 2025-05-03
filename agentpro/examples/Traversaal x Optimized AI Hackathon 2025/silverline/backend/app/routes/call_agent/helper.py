# app\routes\call_agent\helper.py

import json
import time
import dotenv
import asyncio
import aiohttp
from config import CONFIG
from typing import Optional
from fastapi import WebSocket
from agentpro import AgentPro
from datetime import datetime
from openai import AsyncOpenAI
from app.utils.logging.logger import LOG
from agentpro.tools import AresInternetTool
from app.routes.call_agent.dtos import SessionRequest
from websockets.asyncio.client import ClientConnection

# ----------------------------------------------------------
# OpenAI Client
# ----------------------------------------------------------

openai_client = AsyncOpenAI(api_key=CONFIG.openai_api_key)

# ----------------------------------------------------------
# Internet Search Tool Definition
# ----------------------------------------------------------

internet_search_tool = {
    "type": "function",
    "name": "internet_search",
    "description": "Performs a real-time internet search based on the user's query.",
}

# ----------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------

async def extract_voice_name(voice_identifier: str) -> str:
    """Extract clean voice name from identifier string."""
    if voice_identifier.startswith("openai-f-"):
        return voice_identifier.replace("openai-f-", "").lower()
    elif voice_identifier.startswith("openai-m-"):
        return voice_identifier.replace("openai-m-", "").lower()
    return voice_identifier.lower()

async def close_websocket_connections(
    reason: str,
    openai_ws: Optional[ClientConnection],
    client_ws: Optional[WebSocket],
) -> None:
    """Close OpenAI and client WebSocket connections."""
    LOG.info(f"Closing WebSocket connections due to: {reason}")

    # Sending disconnection message to the client
    try:
        await client_ws.send_json({"type": "socket_disconnection", "reason": reason})
        time.sleep(3)
    except Exception as e:
        LOG.warning(f"Error sending disconnection message to client WebSocket: {e}")

    # Close the OpenAI WebSocket connection
    if openai_ws is not None:
        try:
            await openai_ws.close()
            LOG.info("Closed OpenAI WebSocket connection")
        except Exception as e:
            LOG.warning(f"Error closing OpenAI WebSocket: {e}")

    # Close the client WebSocket connection
    if client_ws is not None:
        try:
            await client_ws.close()
            LOG.info("Closed client WebSocket connection")
        except RuntimeError as e:
            LOG.warning(f"Client WebSocket already closed: {e}")

    LOG.info("WebSocket session ended")

async def close_after_timeout(
    delay_seconds: int,
    openai_ws: Optional[ClientConnection],
    client_ws: Optional[WebSocket],
) -> None:
    """Force-close WebSockets after specified timeout."""
    await asyncio.sleep(delay_seconds)
    await close_websocket_connections(
        f"Time limit of {delay_seconds} seconds reached. Closing connections.",
        openai_ws,
        client_ws
    )

async def call_openai_api(prompt: str, validation_schema=None, model=None, max_attempts: int = 3):
    """Call OpenAI API with retry mechanism and response validation."""
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        try:
            LOG.info(f"Calling OpenAI API (Attempt {attempt}/{max_attempts})")
            # Prepare the messages payload
            messages_payload = [{"role": "user", "content": prompt}]
            
            # Call the OpenAI API
            response = await openai_client.chat.completions.create(
                model=model or CONFIG.classifier_model,
                temperature=0.9,
                messages=messages_payload,
                response_format={"type": "json_object"},
            )
            
            # Extract message content
            response_content = response.choices[0].message.content
            LOG.info(f"OpenAI Response: {response_content}")
            
            # Extract usage details
            usage = {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            # Validate JSON structure if schema is provided
            response_json = json.loads(response_content)
            if validation_schema:
                validated_response = validation_schema(**response_json)
                LOG.info("Response structure validated successfully")
            
            return response_content, usage
            
        except Exception as e:
            LOG.error(f"API call attempt {attempt} failed: {e}")
            if attempt < max_attempts:
                LOG.info(f"Retrying API call (Attempt {attempt+1}/{max_attempts})")
                await asyncio.sleep(1)  # Short delay between retries
            else:
                LOG.error(f"All {max_attempts} API call attempts failed")
                raise  # Re-raise the last exception

async def fetch_and_validate_mock_response(agent_id: str) -> dict:
    """Fetch and validate JSON from mock API."""
    url = "http://localhost:8000/ai/mock-api-for-agent-test/response"
    params = {"agent_id": agent_id}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()

        # Validate and parse the received JSON
        session_request = SessionRequest(**data)
        return session_request.model_dump()
    except Exception as e:
        LOG.error(f"Error fetching or validating JSON from API: {e}")
        return {}

# ----------------------------------------------------------
# OpenAI Interaction Functions
# ----------------------------------------------------------

async def initial_settings_openai(openai_ws: ClientConnection, prompt: str, voice_model_name: str) -> None:
    """Send initial session settings to OpenAI WebSocket."""
    session_update = {
        "type": "session.update",
        "session": {
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "instructions": prompt,
            "voice": voice_model_name,
            "turn_detection": {
                "type": "server_vad",
            },
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "tools": [internet_search_tool],
        }
    }
    await openai_ws.send(json.dumps(session_update))

async def user_message_to_openai(openai_ws: ClientConnection, message: str) -> None:
    """Send user message to OpenAI and trigger response."""
    user_message = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {"type": "input_text", "text": message}
            ]
        }
    }
    await openai_ws.send(json.dumps(user_message))

    # Trigger response from OpenAI
    await openai_ws.send(json.dumps({"type": "response.create"}))

# ----------------------------------------------------------
# AgentPro and Internet Search
# ----------------------------------------------------------

async def agentpro_call(user_query):
    """Execute query using AgentPro with internet search capability."""
    dotenv.load_dotenv()
    tools = [AresInternetTool()]
    agent = AgentPro(tools=tools)
    LOG.info("AgentPro is initialized and ready with AresInternetTool")
    try:
        response = agent(user_query)
        return response
    except Exception as e:
        LOG.error(f"Error: {e}")

async def internet_search_func(openai_ws: ClientConnection, lang: str, user_query: str, call_id: str) -> None:
    # Call the internet search tool
    LOG.info("--------------------------------")
    LOG.info("Calling AgentPro")
    user_query += f"\nuse the internet search tool to find the answer to this question your response language should be {lang}."
    agent_response = await agentpro_call(user_query)
    LOG.info(f"AgentPro Final Response ---> {agent_response}")
    LOG.info("--------------------------------")

    payload = {
        "type": "conversation.item.create",
        "item": {
            "type": "function_call_output",
            "call_id": call_id,
            "output": f"this is the response from internet search: {agent_response}"
        }
    }

    LOG.info("Sending internet search response to OpenAI")
    await openai_ws.send(json.dumps(payload))




# async def internet_search_func(openai_ws: ClientConnection, lang: str, user_query: str) -> None:
#     """Execute internet search and forward results to OpenAI."""
#     language_line = f"\nYour communication language will be: {lang} no matter what the language user speaks."

#     instructions = """
#                 Respond with: 'let me check the internet for you'
#             """

#     instructions_with_lang_line = instructions + "\n" + language_line

#     LOG.info("Language line also added to internet_search_func()'s instructions")
    
#     payload = {
#         "type": "response.create",
#         "response": {
#             "instructions": instructions_with_lang_line,
#         }
#     }
#     LOG.info("Sending instructions to OpenAI")
#     await openai_ws.send(json.dumps(payload))
#     LOG.info("Finished sending instructions")

#     # Call the internet search tool
#     LOG.info("Calling AgentPro")
#     agent_response = await agentpro_call(user_query)
#     LOG.info(f"AgentPro Response: {agent_response}")

#     payload = {
#         "type": "response.create",
#         "response": {
#             "instructions": f"this is the response from internet search: {agent_response}",
#         }
#     }

#     LOG.info("Sending instructions to OpenAI")
#     await openai_ws.send(json.dumps(payload))

# ----------------------------------------------------------
# Prompt Construction Functions
# ----------------------------------------------------------

async def construct_regex_prompt(json_data: dict) -> str:
    """Build prompt for end-call scenarios with exact ending messages."""
    regex_prompt = """
## Conversation Management - CRITICAL RULE

## ENDING MESSAGES MUST BE USED EXACTLY AS WRITTEN - NO VARIATIONS ALLOWED
"""
    for idx, scenario in enumerate(json_data["endCallScenarios"], 1):
        regex_prompt += f"""
{idx}. {scenario['scenario']}:
   - EXACT RESPONSE ONLY: {scenario['responseForRegex']}
   - NO OTHER TEXT PERMITTED
"""
    return regex_prompt

async def construct_internet_search_prompt(json_data: dict) -> str:
    """Build prompt for internet search scenarios."""
    internet_search_prompt = """

## You Have The Ability To Call Tools And Functions To Assist With The Conversation.
    
## Internet Search Management - CRITICAL RULE

## IF THESE SCENARIOS OCCUR, IMMEDIATELY CALL THIS FUNCTION/TOOL: internet_search_func()
"""
    for idx, scenario in enumerate(json_data.get("internetSearchScenarios", []), 1):
        internet_search_prompt += f"""
{idx}. {scenario['scenario']}
   - ACTION: Call internet_search_func()
"""
    return internet_search_prompt

# ----------------------------------------------------------
# Complex Composite Functions
# ----------------------------------------------------------

async def append_prompt_scenarios(mock_resp: dict) -> tuple[dict, list[str]]:
    """Append scenario instructions to prompt and collect ending messages."""
    ending_messages_for_regex = []

    # End call scenarios
    if mock_resp.get("endCallScenarios"):
        LOG.info("End call scenarios found in the JSON from backend")
        regex_prompt = await construct_regex_prompt(mock_resp)
        LOG.info("Constructed regex prompt for end_call_scenarios")
        mock_resp["instructions"] = mock_resp.get("instructions", "") + "\n" + regex_prompt

        # Gather ending messages
        LOG.info("Extracting ending messages for regex")
        for scenario in mock_resp["endCallScenarios"]:
            if scenario.get("responseForRegex"):
                ending_messages_for_regex.append(scenario["responseForRegex"].lower())

    # Internet search scenarios
    if mock_resp.get("internetSearchScenarios"):
        LOG.info("Internet search scenarios found in the JSON from backend")
        internet_search_prompt = await construct_internet_search_prompt(mock_resp)
        LOG.info("Constructed internet search prompt")
        mock_resp["instructions"] = (
            mock_resp.get("instructions", "") + "\n" + internet_search_prompt
        )

    # Handle AI Initiates with Defined Message
    if mock_resp.get("initiationMode") == "AI Initiates (Defined Message)":
        defined_message = mock_resp.get("aiDefinedMessage", "Hello!")
        # Append the special instruction to the prompt
        new_line = f"\nRemember that after user says Hello Your first reply will strictly will be: {defined_message}"
        mock_resp["instructions"] = mock_resp.get("instructions", "") + new_line

        LOG.info(f"Appended 'Your first message will be: {defined_message}' to the prompt.")

    # Set communication language
    if mock_resp.get("language"):
        lang = mock_resp.get("language", "en-US")
        # Append the language instruction to the prompt
        new_line = f"\nYour communication language will be: {lang} no matter what the language user speaks."
        mock_resp["instructions"] = mock_resp.get("instructions", "") + new_line

        LOG.info(f"AI communication language set to: '{lang}'")

    return mock_resp, ending_messages_for_regex

async def insert_call_metadata_into_database(call_metadata: dict) -> None:
    """Insert call metadata into database using Prisma client."""
    # Handle datetime conversion - the datetime might be an ISO string that needs to be parsed
    datetime_value = call_metadata.get("datetime")
    if isinstance(datetime_value, str):
        try:
            # Convert ISO string to datetime object
            datetime_value = datetime.fromisoformat(datetime_value)
        except Exception as e:
            LOG.error(f"Error parsing datetime string: {e}")
            # Fallback to current time if parsing fails
            datetime_value = datetime.now()
    
    prepared_call_metadata = {
        "datetime": datetime_value,  # Now should be a proper datetime object
        "callerId": call_metadata.get("caller_id"),
        "callerNumber": call_metadata.get("caller_number"),
        "twilioNumber": call_metadata.get("twilio_number"),
        "callDuration": call_metadata.get("call_duration"),
        "type": call_metadata.get("type"),
        "isSpam": call_metadata.get("is_spam"),
        "reason": call_metadata.get("reason")
    }

    try:
        from app.db.prisma_client import prisma_client
        
        # Add some debug logging to see what's being sent
        LOG.info(f"Prepared call metadata for database: {prepared_call_metadata}")
        
        # Insert the record into the database - update to use CallHistory (matching schema case)
        result = await prisma_client.callhistory.create(
            data=prepared_call_metadata
        )
        
        LOG.info(f"Call metadata inserted into database with ID: {result.id}")
        
        return result.id
    except Exception as e:
        LOG.error(f"Error inserting call metadata into database: {e}")
        # Log the exact error for debugging
        LOG.error(f"Exception details: {str(e)}")
        return {}