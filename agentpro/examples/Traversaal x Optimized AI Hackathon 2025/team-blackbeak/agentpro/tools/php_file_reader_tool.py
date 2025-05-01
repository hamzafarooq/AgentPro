from agentpro.tools.base import Tool

class PHPFileReaderTool(Tool):
    name: str = "PHPFileReaderTool"
    description: str = "Reads the content of a PHP file and returns it as raw text"
    arg: str = "Content of a .php file as text"

    def run(self, file_content: str) -> str:
        return file_content if file_content else "No content in file."
