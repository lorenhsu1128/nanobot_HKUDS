"""
LSP Manager for coordinating multiple language servers.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Optional

from loguru import logger

from nanobot.config.schema import LSPConfig
from nanobot.lsp.client import LSPClient


class LSPManager:
    """
    Manages multiple LSP clients (one per language).
    """

    def __init__(self, config: Dict[str, LSPConfig], workspace_root: Path):
        self.config = config
        self.workspace_root = workspace_root
        self.clients: Dict[str, LSPClient] = {}
        
        # Basic extension mapping
        # TODO: Make this configurable
        self.ext_map = {
            ".py": "python",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
            ".rs": "rust",
            ".go": "go",
            ".c": "c",
            ".cpp": "cpp",
            ".java": "java",
        }

    async def get_client_for_file(self, file_path: str) -> Optional[LSPClient]:
        """Get or start a client for the given file."""
        ext = os.path.splitext(file_path)[1]
        language_id = self.ext_map.get(ext)
        
        if not language_id:
            return None
        
        return await self.get_client(language_id)

    async def get_client(self, language_id: str) -> Optional[LSPClient]:
        """Get or start a client for the given language."""
        if language_id in self.clients:
            return self.clients[language_id]

        if language_id not in self.config:
            # logger.debug(f"No LSP config for {language_id}")
            return None

        cfg: LSPConfig = self.config[language_id]
        
        try:
            client = LSPClient(
                command=cfg.command,
                args=cfg.args,
                root_uri=cfg.root_uri or Path(self.workspace_root).as_uri(),
                env=os.environ.copy() | cfg.env
            )
            await client.start()
            self.clients[language_id] = client
            return client
        except Exception as e:
            logger.error(f"Failed to start LSP for {language_id}: {e}")
            return None

    async def shutdown(self) -> None:
        """Stop all running clients."""
        logger.info("Shutting down LSP servers...")
        tasks = []
        for client in self.clients.values():
            tasks.append(client.stops())
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.clients.clear()
