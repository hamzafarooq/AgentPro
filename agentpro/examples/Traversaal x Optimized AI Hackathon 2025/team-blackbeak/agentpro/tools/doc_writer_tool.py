from agentpro.tools.base import Tool
from agentpro.tools.mistral_client import MistralClient

class DocWriterTool(Tool):
    name: str = "DocWriterTool"
    description: str = "Creates a README.md from project code"
    arg: str = "Source code or project structure"

    def run(self, code: str) -> str:
        prompt = f"Generate a complete README.md for a Next.js project built from this code:\n```\n{code}\n```"
        return MistralClient.query(prompt)
