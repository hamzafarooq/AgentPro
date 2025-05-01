from agentpro.tools.base import Tool
from agentpro.tools.mistral_client import MistralClient

class SecurityTool(Tool):
    name: str = "SecurityTool"
    description: str = "Analyzes vulnerabilities in PHP or JS code"
    arg: str = "PHP/JS source code"

    def run(self, code: str) -> str:
        prompt = f"""
        You are a security expert. Analyze this code and provide potential vulnerabilities with solutions:
        ```
        {code}
        ``` 
        The output must be in markdown format.
        """
        return MistralClient.query(prompt)
