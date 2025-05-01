from typing import Any
from abc import ABC, abstractmethod
from pydantic import BaseModel

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
