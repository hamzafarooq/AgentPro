from agentpro.tools.base import Tool
from agentpro.tools.mistral_client import MistralClient

class PHPAuditTool(Tool):
    name: str = "PHPAuditTool"
    description: str = "Analyzes PHP applications and provides detailed reports"
    arg: str = "PHP source code"

    def run(self, php_input: str) -> str:
        prompt = f"""
        You are a PHP application analysis expert. Your role is to provide detailed and structured reports on PHP applications submitted by users.

        Systematically structure your analyses as follows:

        ## Complete Analysis Report

        1. PHP Application Analysis
        2. Features
        3. Project Structure
        4. Interface Overview
        5. Interface Components
        6. Database
        7. Conclusion

        Maintain a professional and technical tone while remaining accessible to intermediate PHP developers.

        Provided application:
        ```php
        {php_input}
        ```
        
        The output must be in markdown format.
        """

        return MistralClient.query(prompt)

