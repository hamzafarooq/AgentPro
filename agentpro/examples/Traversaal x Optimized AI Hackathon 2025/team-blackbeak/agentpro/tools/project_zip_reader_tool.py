from agentpro.tools.base import Tool
import zipfile
import tempfile
import os

class ProjectZipReaderTool(Tool):
    name: str = "ProjectZipReaderTool"
    description: str = "Extracts PHP content from files in a ZIP archive"
    arg: str = "ZIP file containing .php files"

    def run(self, zip_file) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(tmp)
            php_contents = []
            for root, _, files in os.walk(tmp):
                for file in files:
                    if file.endswith(".php"):
                        path = os.path.join(root, file)
                        with open(path, encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            php_contents.append(f"// File: {file}\n{content}\n")
            return "\n\n".join(php_contents) or "No PHP files detected."
