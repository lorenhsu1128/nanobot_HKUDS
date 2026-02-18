
import asyncio
import os
from pathlib import Path
from nanobot.config.loader import load_config
from nanobot.lsp.manager import LSPManager
from nanobot.agent.tools.lsp import LSPDefinitionTool

async def test_lsp():
    # Set config path env var
    os.environ["NANOBOT_CONFIG_PATH"] = str(Path("test_lsp_config.json").absolute())
    
    config = load_config()
    workspace = Path.cwd()
    
    print(f"Loading config from {os.environ['NANOBOT_CONFIG_PATH']}")
    print(f"LSP Config: {config.tools.lsp}")
    
    lsp_manager = LSPManager(config.tools.lsp, workspace)
    
    # Create a dummy python file to test definition
    test_file = workspace / "test_def.py"
    test_file.write_text("def hello():\n    pass\n\nhello()", encoding="utf-8")
    
    try:
        print("Starting LSP Definition Tool test...")
        tool = LSPDefinitionTool(lsp_manager)
        
        # Test finding definition of hello() on line 4
        # hello() is defined on line 1
        result = await tool.execute(str(test_file), 4, 0)
        print(f"LSP Result: {result}")
        
        if "range" in str(result) and "uri" in str(result):
            print("SUCCESS: LSP returned a valid definition result.")
        else:
            print("FAILURE: LSP did not return a valid result.")
            
    finally:
        await lsp_manager.shutdown()
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    asyncio.run(test_lsp())
