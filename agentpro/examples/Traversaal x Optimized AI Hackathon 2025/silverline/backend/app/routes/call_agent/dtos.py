# app\routes\call_agent\dtos.py

from enum import StrEnum
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.utils.base_schema.base_schema import BaseResponse

# --------------------------------------------------------------------------
# Call Classification Schema
# --------------------------------------------------------------------------

class CallType(StrEnum):
    MEDICAL_HEALTH : str = "MEDICAL_HEALTH"
    ENVIRONMENTAL : str = "ENVIRONMENTAL"
    EMOTIONAL_DISTRESS : str = "EMOTIONAL_DISTRESS"
    DAILY_LIVING : str = "DAILY_LIVING"
    OTHER : str = "OTHER"
    NOT_SURE : str = "NOT_SURE"

class IsSpam(StrEnum):
    SPAM : str = "SPAM"
    NOT_SPAM : str = "NOT_SPAM"
    NOT_SURE : str = "NOT_SURE"

class CallClassification(BaseModel):
    is_spam: IsSpam
    reason: str
    type: CallType

class CallMetadata(BaseModel):
    datetime: datetime  # Date and time when the call occurred
    caller_id: Optional[str] = None  # Unique identifier for the caller
    caller_number: Optional[str] = None  # Phone number of the caller
    twilio_number: Optional[str] = None  # Twilio phone number that call was received on
    call_duration: Optional[int] = None  # Duration of the call in seconds
    type: Optional[CallType] = None  # Type of call (Medical, Environmental, etc.)
    is_spam: Optional[IsSpam] = None  # Whether the call is spam or not
    reason: Optional[str] = None  # Reason or summary of the call


# --------------------------------------------------------------------------
# Mock Json Schema
# --------------------------------------------------------------------------

class InitiationMode(StrEnum):
    user_initiates = "User Initiates"
    ai_initiates_dynamic = "AI Initiates (Dynamic Message)"
    ai_initiates_defined = "AI Initiates (Defined Message)"

class VoiceModelName(StrEnum):
    openai_m_Verse = "verse"
    openai_m_Echo = "echo"
    openai_m_Ballad = "ballad"
    openai_m_Ash = "ash"
    openai_f_Shimmer = "shimmer"
    openai_f_Sage = "sage"
    openai_f_Coral = "coral"
    openai_f_Alloy = "alloy"

class EndCallScenario(BaseModel):
    id: Optional[int] = None
    scenario: Optional[str] = None
    responseForRegex: Optional[str] = None

class InternetSearchScenario(BaseModel):
    id: Optional[int] = None
    scenario: Optional[str] = None

class SessionRequest(BaseModel):
    language: str = "en-US"
    id: Optional[int] = None
    voiceModelName: VoiceModelName = VoiceModelName.openai_f_Alloy
    aiDefinedMessage: Optional[str] = None
    modalities: List[str] = ['audio', 'text']
    instructions: str = "You are a helpful assistant"
    endCallScenarios: Optional[List[EndCallScenario]] = None
    internetSearchScenarios: Optional[List[InternetSearchScenario]] = None
    initiationMode: InitiationMode = InitiationMode.ai_initiates_dynamic
    sessionTimeoutInSeconds: int = 20