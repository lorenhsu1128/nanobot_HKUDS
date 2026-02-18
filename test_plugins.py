
import asyncio
import os
import sys
from pathlib import Path
from nanobot.config.loader import load_config
from nanobot.agent.loop import AgentLoop
from nanobot.providers.factory import ProviderFactory

# Add current dir to sys.path so we can import my_custom_tool
sys.path.append(str(Path.cwd()))

async def test_plugins():
    os.environ["NANOBOT_CONFIG_PATH"] = str(Path("test_plugin_config.json").absolute())
    
    config = load_config()
    print(f"Custom tools config: {config.tools.custom}")
    
    # Create dummy provider
    from nanobot.providers.litellm_provider import LiteLLMProvider
    provider = LiteLLMProvider(api_key="sk-dummy", default_model="gpt-3.5-turbo", provider_name="openai")
    
    # Mock bus
    class MockBus:
        def __init__(self):
            self.publish_outbound = lambda x: None
            self.consume_outbound = lambda: asyncio.sleep(0.1)
            
    bus = MockBus()
    
    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=Path.cwd(),
        custom_tools=config.tools.custom
    )
    
    # Check if tool is registered
    if agent.tools.has("custom_hello"):
        print("SUCCESS: 'custom_hello' tool is registered.")
        result = await agent.tools.execute("custom_hello", {"name": "World"})
        print(f"Tool Result: {result}")
        if "Start Custom Hello World End Custom Hello" in result:
             print("SUCCESS: Tool execution verified.")
        else:
             print("FAILURE: Tool output mismatch.")
    else:
        print("FAILURE: 'custom_hello' tool NOT found.")

if __name__ == "__main__":
    asyncio.run(test_plugins())
