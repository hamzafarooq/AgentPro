from typing import List
from agentpro.tools.base import Tool

class AgentPro:
    def __init__(self, tools: List[Tool]):
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    def __call__(self, prompt: str) -> str:
        for tool in self.tools:
            try:
                print(f"Using tool: {tool.name}")
                result = tool.run(prompt)
                if result:
                    return result
            except Exception as e:
                print(f"Error with tool {tool.name}: {e}")
                continue

        return "No tool could process the request."
        

    def list_tools(self):
        return [tool.get_tool_description() for tool in self.tools]
