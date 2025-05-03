# backend\app\routes\log_viewer\log_viewer.py

import json
import tempfile
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter, Query, HTTPException
from app.routes.log_viewer.log_viewer_service import read_log_file


tag: str = "Log Viewer"
log_router = APIRouter(tags=[tag], prefix="/server")


@log_router.get("/send-logs")
def send_logs(date: str = Query("today", description="Date in YYYY-MM-DD format or 'today'")):
    try:
        logs, date = read_log_file(date)
        
        if not logs:
            raise HTTPException(status_code=404, detail=f"No logs found for the specified date: {date}")
        
        # Extract all possible keys from logs (same as in view_logs)
        all_keys = set()
        for log in logs:
            all_keys.update(log.keys())
        headers = sorted(list(all_keys))  # Sort headers for consistency
        
        # Format the date for response
        if date == "today":
            formatted_date = datetime.today().strftime("%Y-%m-%d")
        else:
            formatted_date = date
        
        # Return the logs directly as JSON with headers
        return JSONResponse(content={
            "date": formatted_date,
            "logs": logs,
            "headers": headers
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    








