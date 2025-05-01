from agentpro.tools.base import Tool
from agentpro.tools.mistral_client import MistralClient

class PHPAnalyzerTool(Tool):
    name: str = "PHP Analyzer"
    description: str = "Modernize legacy PHP code into a scalable Next.js 14 architecture with the help of Mistral Codestral."
    arg: str = "PHP code as string"

    def run(self, php_code: str) -> str:
        prompt = f"""
        Convert the following PHP code into a modern application using Next.js 14:

        ```php
        {php_code}
        ```
        
        Objectives:
        - Create a React component for the frontend (forms, etc.)
        - Use API routes (`/pages/api/...`) to handle backend (email, database, etc.)
        - Use `getServerSideProps` or `fetch()` if needed
        - Keep the code clean, commented, and modular

        Make sure to use Next.js best practices (React, API routes, server-side fetch when necessary).
        
        The output must be in markdown format.
        """

        return MistralClient.query(prompt)


