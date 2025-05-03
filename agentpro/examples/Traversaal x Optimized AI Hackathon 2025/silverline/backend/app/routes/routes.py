from config import CONFIG
from fastapi import APIRouter
from app.routes.dashboard.apis import dashboard_router
from app.routes.call_agent.apis import websocket_twilio_apis_router
from app.routes.call_agent.backend_mock_apis import mock_backend_api_router
from app.routes.log_viewer.log_viewer import log_router

MAIN_ROUTER = APIRouter(prefix=CONFIG.root_path)

# Add a health check endpoint
@MAIN_ROUTER.get("/health")
async def health_check():
    """Health check endpoint for monitoring and diagnostics"""
    return {"status": "ok", "message": "API server is running"}

MAIN_ROUTER.include_router(dashboard_router)

MAIN_ROUTER.include_router(mock_backend_api_router)

MAIN_ROUTER.include_router(websocket_twilio_apis_router)

MAIN_ROUTER.include_router(log_router)