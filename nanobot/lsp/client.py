"""
LSP Client implementation for Nanobot.
Handles JSON-RPC communication with Language Servers over stdio.
"""

import asyncio
import json
import os
from typing import Any, Dict, Optional
from dataclasses import dataclass

from loguru import logger


@dataclass
class LSPResponse:
    id: Optional[int]
    result: Any
    error: Optional[Dict[str, Any]]


class LSPClientError(Exception):
    """Base error for LSP client."""
    pass


class LSPClient:
    """
    A lightweight LSP client that communicates via stdio.
    """

    def __init__(
        self,
        command: str,
        args: list[str],
        root_uri: str,
        env: Optional[Dict[str, str]] = None
    ):
        self.command = command
        self.args = args
        self.root_uri = root_uri
        self.env = env or os.environ.copy()
        
        self.process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0
        self._pending_requests: Dict[int, asyncio.Future] = {}
        self._reader_task: Optional[asyncio.Task] = None
        self.capabilities: Dict[str, Any] = {}
        self.shutdown_received = False

    async def start(self) -> None:
        """Start the LSP server subprocess."""
        try:
            logger.info(f"Starting LSP server: {self.command} {self.args}")
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=self.env
            )
            self._reader_task = asyncio.create_task(self._read_loop())
            await self._initialize()
        except Exception as e:
            logger.error(f"Failed to start LSP server: {e}")
            raise LSPClientError(f"Failed to start LSP server: {e}")

    async def stops(self) -> None:
        """Stop the LSP server."""
        if self._reader_task:
            self._reader_task.cancel()
        
        if self.process:
            try:
                # Proper shutdown sequence
                if not self.shutdown_received:
                    await self.send_request("shutdown", None)
                    await self.send_notification("exit", None)
            except Exception:
                pass
            
            if self.process.returncode is None:
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    self.process.kill()

    async def send_request(self, method: str, params: Any) -> Any:
        """Send a JSON-RPC request and wait for the result."""
        if not self.process:
            raise LSPClientError("Server not running")

        self._request_id += 1
        req_id = self._request_id
        
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params
        }
        
        future = asyncio.get_running_loop().create_future()
        self._pending_requests[req_id] = future
        
        await self._send_payload(payload)
        
        try:
            # Wait for response with timeout
            return await asyncio.wait_for(future, timeout=10.0)
        except asyncio.TimeoutError:
            self._pending_requests.pop(req_id, None)
            raise LSPClientError(f"Request {method} timed out")

    async def send_notification(self, method: str, params: Any) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process:
            return

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        await self._send_payload(payload)

    async def _send_payload(self, payload: Dict[str, Any]) -> None:
        """Encode and write payload to server stdin."""
        content = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(content)}\r\n\r\n".encode("ascii")
        
        if self.process and self.process.stdin:
            self.process.stdin.write(header + content)
            await self.process.stdin.drain()

    async def _initialize(self) -> None:
        """Perform LSP handshake."""
        params = {
            "processId": os.getpid(),
            "rootUri": self.root_uri,
            "capabilities": {
                "textDocument": {
                    "synchronization": {
                        "didSave": True,
                        "willSave": False
                    },
                    "hover": {"contentFormat": ["markdown", "plaintext"]},
                    "definition": {"linkSupport": True}
                }
            }
        }
        
        response = await self.send_request("initialize", params)
        self.capabilities = response.get("capabilities", {})
        await self.send_notification("initialized", {})
        logger.info(f"LSP Initialized. Capabilities: {self.capabilities.keys()}")

    async def _read_loop(self) -> None:
        """Read Loop for handling stdout from server."""
        if not self.process or not self.process.stdout:
            return
            
        buffer = b""
        while True:
            try:
                # Read headers
                content_length = 0
                while True:
                    line = await self.process.stdout.readline()
                    if not line:
                        break
                    
                    line_str = line.decode("ascii", errors="replace").strip()
                    if not line_str:
                        # Empty line marks end of headers
                        break
                    
                    if line_str.startswith("Content-Length:"):
                        try:
                            content_length = int(line_str.split(":", 1)[1].strip())
                        except ValueError:
                            pass
                
                if content_length == 0:
                    continue
                
                # Read body
                body = await self.process.stdout.readexactly(content_length)
                try:
                    message = json.loads(body)
                    self._handle_message(message)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode JSON from LSP: {body[:50]}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in LSP read loop: {e}")
                break

    def _handle_message(self, message: Dict[str, Any]) -> None:
        """Dispatch incoming message."""
        if "id" in message:
            # Response to a request
            req_id = message["id"]
            if req_id in self._pending_requests:
                future = self._pending_requests.pop(req_id)
                if not future.done():
                    if "error" in message:
                        future.set_exception(LSPClientError(str(message["error"])))
                    else:
                        future.set_result(message.get("result"))
        else:
            # Notification from server (e.g. diagnostics)
            self._handle_notification(message)

    def _handle_notification(self, message: Dict[str, Any]) -> None:
        """Handle notifications (like textDocument/publishDiagnostics)."""
        method = message.get("method")
        params = message.get("params")
        
        if method == "textDocument/publishDiagnostics":
            # For now, just log. In future, we can store these in the Manager.
            # logger.debug(f"Diagnostics for {params.get('uri')}: {len(params.get('diagnostics', []))} items")
            pass
        elif method == "window/showMessage":
            logger.info(f"LSP Message ({params.get('type')}): {params.get('message')}")
        elif method == "window/logMessage":
            logger.debug(f"LSP Log ({params.get('type')}): {params.get('message')}")

    # --- Standard LSP Features ---

    async def text_document_did_open(self, file_path: str, language_id: str, content: str) -> None:
        uri = self._path_to_uri(file_path)
        await self.send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": language_id,
                "version": 1,
                "text": content
            }
        })

    async def text_document_definition(self, file_path: str, line: int, character: int) -> Any:
        uri = self._path_to_uri(file_path)
        return await self.send_request("textDocument/definition", {
            "textDocument": {"uri": uri},
            "position": {"line": line - 1, "character": character}
        })
    
    async def text_document_references(self, file_path: str, line: int, character: int) -> Any:
        uri = self._path_to_uri(file_path)
        return await self.send_request("textDocument/references", {
            "textDocument": {"uri": uri},
            "position": {"line": line - 1, "character": character},
            "context": {"includeDeclaration": True}
        })

    async def text_document_hover(self, file_path: str, line: int, character: int) -> Any:
        uri = self._path_to_uri(file_path)
        return await self.send_request("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": line - 1, "character": character}
        })

    def _path_to_uri(self, path: str) -> str:
        from urllib.parse import quote
        path = os.path.abspath(path).replace("\\", "/")
        return f"file:///{quote(path)}"
