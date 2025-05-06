from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict
from openai import OpenAI
import os
class Tool(ABC, BaseModel):
    name: str
    description: str
    arg: str
    def model_post_init(self, __context: Any) -> None:
        self.name = self.name.lower().replace(' ', '_')
        self.description = self.description.lower()
        self.arg = self.arg.lower()
    @abstractmethod
    def run(self, prompt: str) -> str:
        pass
    def get_tool_description(self):
        return f"Tool: {self.name}\nDescription: {self.description}\nArg: {self.arg}\n"
class LLMTool(Tool):
    client: Any = None   
    def __init__(self, **data):
        super().__init__(**data)
        if self.client is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set") # OPTIONAL : TAKE API-KEY AS INPUT AT THIS STAGE
            self.client = OpenAI(api_key=api_key)
