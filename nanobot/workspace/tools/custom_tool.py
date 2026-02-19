
import random
from nanobot.agent.tools.base import Tool

class RandomNumberTool(Tool):
    """A simple tool that generates a random number."""
    
    name = "generate_random_number"
    description = "Generates a random number between a minimum and maximum value."
    parameters = {
        "type": "object",
        "properties": {
            "min_val": {
                "type": "integer", 
                "description": "Minimum value (inclusive)"
            },
            "max_val": {
                "type": "integer", 
                "description": "Maximum value (inclusive)"
            }
        },
        "required": ["min_val", "max_val"]
    }

    async def execute(self, min_val: int = 0, max_val: int = 100) -> str:
        """
        Execute the tool.
        
        Args:
            min_val: Minimum integer value.
            max_val: Maximum integer value.
            
        Returns:
            String containing the random number.
        """
        try:
            val = random.randint(min_val, max_val)
            return str(val)
        except Exception as e:
            return f"Error generating random number: {e}"

if __name__ == "__main__":
    import asyncio
    tool = RandomNumberTool()
    print(asyncio.run(tool.execute(1, 10)))
