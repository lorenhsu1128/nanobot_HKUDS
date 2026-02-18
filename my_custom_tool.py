
from nanobot.agent.tools.base import Tool

class MyCustomTool(Tool):
    name = "custom_hello"
    description = "A custom tool that says hello."
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name to greet"}
        },
        "required": ["name"]
    }

    async def execute(self, name: str) -> str:
        return f"Start Custom Hello {name} End Custom Hello"
