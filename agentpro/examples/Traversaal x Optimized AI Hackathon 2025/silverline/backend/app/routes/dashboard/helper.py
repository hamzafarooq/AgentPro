from typing import List, Dict, Any
from app.db.prisma_client import prisma_client
from app.utils.logging.logger import LOG


async def get_all_calls() -> List[Dict[str, Any]]:
    """Fetch all call history data"""
    calls = await prisma_client.callhistory.find_many()
    
    result = [
        {
            "id": str(call.id),
            "timestamp": call.datetime.isoformat(),
            "type": getattr(call, "type", None),
            "caller_number": getattr(call, "callerNumber", None),
            "twilio_number": getattr(call, "twilioNumber", None),
            "call_duration": getattr(call, "callDuration", None),
            "is_spam": getattr(call, "isSpam", None),
            "reason": getattr(call, "reason", None)
        }
        for call in calls
    ]
    
    LOG.info(f"API Response [/api/calls]: {len(result)} records retrieved")
    return result


async def get_summary_metrics() -> Dict[str, Any]:
    """Get summary metrics for dashboard"""
    # Get total calls
    total_calls = await prisma_client.callhistory.count()
    
    # Get calls by type
    medical_calls = await prisma_client.callhistory.count(
        where={"type": "Medical"}
    )
    
    environmental_calls = await prisma_client.callhistory.count(
        where={"type": "Environmental"}
    )
    
    # Get Other calls directly
    others_calls = await prisma_client.callhistory.count(
        where={"type": "Other"}
    )
    
    result = {
        "totalCalls": {"count": total_calls},
        "medical": {"count": medical_calls},
        "environmental": {"count": environmental_calls},
        "others": {"count": others_calls}
    }
    
    LOG.info(f"API Response [/api/statistics/summary]: retrieved metrics")
    return result


async def get_call_volume(interval: str = "day") -> Dict[str, Any]:
    """Get call volume data for charts"""
    # Get all calls
    calls = await prisma_client.callhistory.find_many(
        order={"datetime": "asc"}
    )
    
    if not calls:
        # Return empty chart data if no calls found
        return {
            "labels": [],
            "datasets": [
                {
                    "label": "Call Volume",
                    "data": []
                }
            ]
        }
    
    # Group calls by date
    date_groups = {}
    call_types = {
        "Medical": 0,
        "Environmental": 0,
        "Emotional": 0,
        "Daily Living": 0,
        "Other": 0,
        "Not Sure": 0
    }
    
    for call in calls:
        # Format date based on interval
        date_str = call.datetime.date().isoformat()  # Use date only
        
        # Initialize if this is the first call for this date
        if date_str not in date_groups:
            date_groups[date_str] = {
                "total": 0,
                "Medical": 0,
                "Environmental": 0,
                "Emotional": 0,
                "Daily Living": 0,
                "Other": 0,
                "Not Sure": 0
            }
        
        # Increment total count for this date
        date_groups[date_str]["total"] += 1
        
        # Increment count for this call type if available
        if call.type:
            date_groups[date_str][call.type] = date_groups[date_str].get(call.type, 0) + 1
            call_types[call.type] = 1  # Mark this call type as having data
    
    # Sort dates
    sorted_dates = sorted(date_groups.keys())
    
    # Create datasets
    datasets = [
        {
            "label": "Call Volume",
            "data": [date_groups[date]["total"] for date in sorted_dates]
        }
    ]
    
    # Add datasets for each call type that has data
    for call_type, has_data in call_types.items():
        if has_data:
            datasets.append({
                "label": call_type,
                "data": [date_groups[date].get(call_type, 0) for date in sorted_dates]
            })
    
    result = {
        "labels": sorted_dates,
        "datasets": datasets
    }
    
    LOG.info(f"API Response [/api/statistics/call-volume]: {len(calls)} calls grouped into {len(sorted_dates)} date points")
    return result


async def get_call_types() -> Dict[str, Any]:
    """Get breakdown of call types"""
    # Get all calls
    calls = await prisma_client.callhistory.find_many()
    
    # Group calls by type
    type_counts = {}
    for call in calls:
        call_type = call.type or "unknown"
        type_counts[call_type] = type_counts.get(call_type, 0) + 1
    
    total_calls = len(calls)
    
    # Create response data
    result_data = []
    for call_type, count in type_counts.items():
        percentage = (count / total_calls * 100) if total_calls > 0 else 0
        result_data.append({
            "name": call_type,
            "value": count,
            "percentage": round(percentage, 2)
        })
    
    result = {"data": result_data}
    LOG.info(f"API Response [/api/statistics/types]: {len(result_data)} call types analyzed")
    return result


async def get_spam_status() -> Dict[str, Any]:
    """Get breakdown of calls by spam status"""
    # Get all calls
    calls = await prisma_client.callhistory.find_many()
    
    # Count calls by spam status
    spam_counts = {
        "SPAM": 0,
        "NOT_SPAM": 0,
        "NOT_SURE": 0
    }
    
    for call in calls:
        # Use the isSpam attribute if available, otherwise count as "NOT_SURE"
        spam_status = getattr(call, "isSpam", "NOT_SURE")
        spam_counts[spam_status] = spam_counts.get(spam_status, 0) + 1
    
    total_calls = len(calls)
    
    # Create response data
    result_data = []
    for status, count in spam_counts.items():
        percentage = (count / total_calls * 100) if total_calls > 0 else 0
        result_data.append({
            "status": status,
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    result = {"data": result_data}
    LOG.info(f"API Response [/api/statistics/spam-status]: {len(result_data)} spam statuses analyzed")
    return result
