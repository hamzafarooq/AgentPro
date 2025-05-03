# backend\app\routes\log_viewer\log_viewer_service.py

import os
import json
from datetime import datetime
from app.utils.logging.logger import LOG_DIRECTORY



def read_log_file(date: str):
    # Format the date to match log file naming convention
    if date != "today":
        date = datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
    

    # Check if the given date matches today's date
    current_date = datetime.now().strftime("%Y-%m-%d")
    if date == current_date:
        date = "today"

    log_file = os.path.join(LOG_DIRECTORY, f"{date}.log")
    
    # If the log file for the specified date does not exist, fallback to today's log
    if not os.path.exists(log_file):
        return [], date

    logs: list[dict] = []
    buffer = ""
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            buffer += line
            try:
                log_entry = json.loads(buffer)
                logs.append(log_entry)
                buffer = ""  # Reset buffer after successful load
            except json.JSONDecodeError:
                buffer += " "  # Add a space and continue accumulating
    return logs, date