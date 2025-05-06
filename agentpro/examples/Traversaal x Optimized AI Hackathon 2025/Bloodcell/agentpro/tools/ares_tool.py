import requests
import os
from pydantic import HttpUrl
from .base import Tool
from typing import Optional

class AresInternetTool(Tool):
    name: str = "Ares Health-Enhanced Internet Search Tool"
    description: str = "Enhanced tool to search healthcare and location-relevant data using Traversaal Ares web search"
    arg: str = "Prompt string, optionally with 'location' for local health-related searches"
    url: HttpUrl = "https://api-ares.traversaal.ai/live/predict"
    x_api_key: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.x_api_key is None:
            self.x_api_key = os.environ.get("TRAVERSAAL_ARES_API_KEY")
            if not self.x_api_key:
                raise ValueError("TRAVERSAAL_ARES_API_KEY environment variable not set")

    def run(self, prompt: str, location: Optional[str] = None) -> str:
        print(f"Running AresHealthEnhancedTool with prompt: {prompt}")

        # Detect healthcare + location intent
        health_keywords = ["hospital", "blood bank", "clinic", "emergency", "medical center", "donation"]
        is_health_query = any(word in prompt.lower() for word in health_keywords)

        # Improve prompt if it's health-related
        if is_health_query and location:
            improved_prompt = f"List of top-rated {prompt.lower()} in {location}. Include contact info or address if possible."
        else:
            improved_prompt = prompt

        return self.query_ares(improved_prompt)

    def query_ares(self, final_prompt: str) -> str:
        payload = {"query": [final_prompt]}
        response = requests.post(
            self.url,
            json=payload,
            headers={
                "x-api-key": self.x_api_key,
                "content-type": "application/json"
            }
        )
        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        data = response.json()
        return data['data']['response_text']
