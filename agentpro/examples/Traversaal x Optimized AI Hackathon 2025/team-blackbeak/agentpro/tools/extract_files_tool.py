from agentpro.tools.base import Tool
from agentpro.tools.mistral_client import MistralClient

class ExtractFilesFromMarkdownTool(Tool):
    name: str = "ExtractFilesFromMarkdownTool"
    description: str = "Uses Mistral to parse markdown and extract file list"
    arg: str = "Generated markdown with code blocks"

    def run(self, markdown: str) -> str:
        prompt = f"""
        You are a developer assistant. Receive a markdown containing file paths and their content as code blocks. Extract all files and return a JSON list in the format:

        [
        {{ "file_name": "<name>", "path": "<path>", "content": "<full_content>" }}
        ]

        Here's the markdown:

        {markdown}
        
        The output must be in markdown format.
        """

        return MistralClient.query(prompt)


