"""
LSP Tools for the agent.
"""

from pathlib import Path
from typing import Any

from nanobot.agent.tools.base import Tool
from nanobot.lsp.manager import LSPManager


class LSPTool(Tool):
    """Base class for LSP tools."""

    def __init__(self, manager: LSPManager):
        self.manager = manager


class LSPDefinitionTool(LSPTool):
    """
    Go to definition for a symbol in a file.
    """
    name = "lsp_definition"
    description = (
        "Find the definition of a symbol at the specified line and character."
        " Returns the file path and range of the definition."
    )
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the file."
            },
            "line": {
                "type": "integer",
                "description": "Line number (1-based)."
            },
            "character": {
                "type": "integer",
                "description": "Character offset (0-based)."
            }
        },
        "required": ["file_path", "line", "character"]
    }

    async def execute(self, file_path: str, line: int, character: int) -> str:
        client = await self.manager.get_client_for_file(file_path)
        if not client:
            return "Error: No LSP server available for this file type."

        try:
            # Open file specifically? Or assume it's open?
            # Ideally we should send didOpen if haven't. For now assume file exists on disk.
            # Reading content for didOpen
            content = Path(file_path).read_text(encoding="utf-8")
            # We don't know lang id easily here without manager help, but client needs it.
            # Manager has ext map.
            ext = Path(file_path).suffix
            lang_id = self.manager.ext_map.get(ext, "plaintext")
            
            await client.text_document_did_open(file_path, lang_id, content)
            
            result = await client.text_document_definition(file_path, line, character)
            return str(result)
        except Exception as e:
            return f"Error: {e}"


class LSPReferencesTool(LSPTool):
    """
    Find references to a symbol.
    """
    name = "lsp_references"
    description = "Find all references to the symbol at the specified position."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the file."
            },
            "line": {
                "type": "integer",
                "description": "Line number (1-based)."
            },
            "character": {
                "type": "integer",
                "description": "Character offset (0-based)."
            }
        },
        "required": ["file_path", "line", "character"]
    }

    async def execute(self, file_path: str, line: int, character: int) -> str:
        client = await self.manager.get_client_for_file(file_path)
        if not client:
            return "Error: No LSP server available for this file type."

        try:
            content = Path(file_path).read_text(encoding="utf-8")
            ext = Path(file_path).suffix
            lang_id = self.manager.ext_map.get(ext, "plaintext")
            await client.text_document_did_open(file_path, lang_id, content)

            result = await client.text_document_references(file_path, line, character)
            return str(result)
        except Exception as e:
            return f"Error: {e}"


class LSPHoverTool(LSPTool):
    """
    Get hover information (type info, docstring).
    """
    name = "lsp_hover"
    description = "Get documentation or type information for the symbol at the position."
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the file."
            },
            "line": {
                "type": "integer",
                "description": "Line number (1-based)."
            },
            "character": {
                "type": "integer",
                "description": "Character offset (0-based)."
            }
        },
        "required": ["file_path", "line", "character"]
    }

    async def execute(self, file_path: str, line: int, character: int) -> str:
        client = await self.manager.get_client_for_file(file_path)
        if not client:
            return "Error: No LSP server available for this file type."

        try:
            content = Path(file_path).read_text(encoding="utf-8")
            ext = Path(file_path).suffix
            lang_id = self.manager.ext_map.get(ext, "plaintext")
            await client.text_document_did_open(file_path, lang_id, content)

            result = await client.text_document_hover(file_path, line, character)
            return str(result)
        except Exception as e:
            return f"Error: {e}"
