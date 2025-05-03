from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
from enum import StrEnum


class CallType(StrEnum):
    MEDICAL_HEALTH = "Medical"
    ENVIRONMENTAL = "Environmental" 
    EMOTIONAL_DISTRESS = "Emotional"
    DAILY_LIVING = "Daily Living"
    OTHER = "Other"
    NOT_SURE = "Not Sure"


class IsSpam(StrEnum):
    SPAM = "SPAM"
    NOT_SPAM = "NOT_SPAM"
    NOT_SURE = "NOT_SURE"


class CallHistoryDTO(BaseModel):
    id: str
    timestamp: str
    type: Optional[str] = None
    caller_number: Optional[str] = None
    twilio_number: Optional[str] = None
    call_duration: Optional[int] = None
    is_spam: Optional[str] = None
    reason: Optional[str] = None


class CountDTO(BaseModel):
    count: int


class SummaryMetricsDTO(BaseModel):
    totalCalls: CountDTO
    medical: CountDTO
    environmental: CountDTO
    others: CountDTO


class DatasetDTO(BaseModel):
    label: str
    data: List[int]


class CallVolumeDTO(BaseModel):
    labels: List[str]
    datasets: List[DatasetDTO]


class TypeBreakdownDTO(BaseModel):
    name: str
    value: int
    percentage: float


class TypeBreakdownResponseDTO(BaseModel):
    data: List[TypeBreakdownDTO]


class SpamStatusItemDTO(BaseModel):
    status: str
    count: int
    percentage: float


class SpamStatusDTO(BaseModel):
    data: List[SpamStatusItemDTO]
