# backend\app\routes\call_agent\backend_mock_apis.py

import json
from typing import Optional
from fastapi import APIRouter
from app.utils.logging.logger import LOG
from app.utils.err.error import InternalServerError

# Constants
tag: str = "Mock API for Agent Onboarding"
mock_backend_api_router: APIRouter = APIRouter(tags=[tag], prefix="/mock-api-for-agent-test")

# Load mock response from backend
try:
    with open("./app/utils/mock_jsons/backend_mock_json_for_agent_onboarding.json", "r") as file:
        mock_response_from_backend = json.load(file)
except FileNotFoundError:
    LOG.error("Mock JSON file not found")
    mock_response_from_backend = {}

@mock_backend_api_router.get("/response", response_model=dict)
async def get_mock_response(agent_id: Optional[str] = "default_agent"):
    """Mock API to send a JSON response."""
    if not mock_response_from_backend:
        raise InternalServerError(detail="Mock JSON file not found or is empty.")
    return mock_response_from_backend
