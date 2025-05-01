from .agent import AgentPro
from agentpro.tools import (
    PHPAnalyzerTool,
    PHPAuditTool, 
    SecurityTool, 
    TestGeneratorTool,
    ExtractFilesFromMarkdownTool,
    DocWriterTool,
    ProjectZipReaderTool,
    IntegrationTool,
    PHPFileReaderTool
)

php_tool = PHPAnalyzerTool()
audit_tool = PHPAuditTool()
file_reader_tool = PHPFileReaderTool()

security_tool = SecurityTool()
test_tool = TestGeneratorTool()

doc_tool = DocWriterTool()
integration_tool = IntegrationTool()
zip_reader_tool = ProjectZipReaderTool()
extract_files_tool = ExtractFilesFromMarkdownTool()

__all__ = [
    'AgentPro',
    'php_tool',
    'audit_tool',
    'security_tool',
    'test_tool',
    'doc_tool',
    'integration_tool',
    'file_reader_tool',
    'zip_reader_tool',
    'extract_files_tool'
           ]
