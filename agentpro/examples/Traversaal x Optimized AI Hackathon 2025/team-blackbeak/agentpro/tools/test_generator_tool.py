from agentpro.tools.base import Tool
from agentpro.tools.mistral_client import MistralClient

class TestGeneratorTool(Tool):
    name: str = "TestGeneratorTool"
    description: str = "Generates unit tests for Next.js code"
    arg: str = "Next.js source code"

    def run(self, code: str) -> str:
        prompt = f"""
        Generate unit tests for this code:
        
        ```js
        {code}
        ```
        The output must be in markdown format.
        """
        return MistralClient.query(prompt)
