from .agent import AgentPro
from typing import Any
from agentpro.tools import AresInternetTool 
ares_tool = AresInternetTool()
__all__ = ['AgentPro', 'ares_tool'] # add more tools when available
