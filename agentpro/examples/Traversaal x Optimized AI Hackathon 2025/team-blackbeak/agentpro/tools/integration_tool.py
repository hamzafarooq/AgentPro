from agentpro.tools.base import Tool
import os
import json
import html
import re
from datetime import datetime

class IntegrationTool(Tool):
    name: str = "IntegrationTool"
    description: str = "Creates all Next.js files from raw extracted JSON (including markdown code blocks)"
    arg: str = "Text containing markdown block or just JSON [{\"file_name\":..., \"path\":..., \"content\":...}]"

    def run(self, file_json: str) -> dict:
        try:
            match = re.search(r"```json\n(.*?)```", file_json, re.DOTALL)
            raw_json = match.group(1).strip() if match else file_json.strip()
            files = json.loads(raw_json)
        except Exception as e:
            return {"log": f"JSON Error: {e}", "path": ""}

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_path = os.path.join("nextjs-migrated-app", timestamp)
        logs = []

        for file in files:
            try:
                path = os.path.join(base_path, file["path"])
                content = html.unescape(file["content"])
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                logs.append(f"{file['path']} created.")
            except Exception as e:
                logs.append(f"Error {file['path']}: {e}")

        return {
            "log": "\n".join(logs),
            "path": base_path
        }
