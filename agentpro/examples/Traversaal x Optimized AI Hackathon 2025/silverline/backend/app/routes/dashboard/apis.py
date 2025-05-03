import asyncio
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends

from .dtos import (
    CallHistoryDTO,
    SummaryMetricsDTO,
    CallVolumeDTO,
    TypeBreakdownResponseDTO,
    CallType,
    SpamStatusDTO
)
from .helper import (
    get_all_calls,
    get_summary_metrics,
    get_call_volume,
    get_call_types,
    get_spam_status
)
from app.utils.logging.logger import LOG

dashboard_router = APIRouter(prefix="/api", tags=["Dashboard Analytics Endpoints"])

# Maximum time to wait for database operations
DB_OPERATION_TIMEOUT = 15  # seconds


async def execute_db_operation(coro, timeout=DB_OPERATION_TIMEOUT):
    """Execute database operation with a timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        LOG.error(f"Database operation timed out after {timeout} seconds")
        raise HTTPException(status_code=504, detail="Database operation timed out")
    except Exception as e:
        LOG.error(f"Database operation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@dashboard_router.get("/calls", response_model=List[CallHistoryDTO])
async def get_calls():
    """
    Fetch all call history data
    """
    LOG.info("API Request [/api/calls]")
    result = await execute_db_operation(get_all_calls())
    return result


@dashboard_router.get("/statistics/summary", response_model=SummaryMetricsDTO)
async def get_stats_summary():
    """
    Returns key statistics: total calls, average response time, and breakdowns by type
    """
    LOG.info("API Request [/api/statistics/summary]")
    result = await execute_db_operation(get_summary_metrics())
    return result


@dashboard_router.get("/statistics/call-volume", response_model=CallVolumeDTO)
async def get_stats_call_volume(
    interval: str = Query("day", description="Interval for data grouping", enum=["day", "week", "month"])
):
    """
    Returns time-based call volume data for visualizing trends
    """
    LOG.info(f"API Request [/api/statistics/call-volume] interval={interval}")
    
    if interval not in ["day", "week", "month"]:
        raise HTTPException(status_code=400, detail="Interval must be one of: day, week, month")
    
    result = await execute_db_operation(get_call_volume(interval=interval))
    return result


@dashboard_router.get("/statistics/types", response_model=TypeBreakdownResponseDTO)
async def get_stats_types():
    """
    Returns a percentage-based breakdown of call types
    """
    LOG.info("API Request [/api/statistics/types]")
    result = await execute_db_operation(get_call_types())
    return result


@dashboard_router.get("/statistics/spam-status", response_model=SpamStatusDTO)
async def get_stats_spam_status():
    """
    Returns a breakdown of calls by spam status
    """
    LOG.info("API Request [/api/statistics/spam-status]")
    result = await execute_db_operation(get_spam_status())
    return result
