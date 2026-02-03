from __future__ import annotations

import asyncio
from typing import Any

from fastmcp import Client

from src.adapters.mcp_stdio.process import MCPStdioConfig


class MCPStdioClient:
    def __init__(self, config: MCPStdioConfig) -> None:
        self._config = config
        self._transport = config.to_transport()
        self._client = Client(self._transport)
        self._lock = asyncio.Lock()

    async def list_tools(self) -> list[dict[str, Any]]:
        async with self._lock:
            async with self._client:
                return await self._client.list_tools()

    async def call_tool(self, name: str, args: dict[str, Any] | None = None) -> Any:
        async with self._lock:
            async with self._client:
                return await self._client.call_tool(name, args or {})
