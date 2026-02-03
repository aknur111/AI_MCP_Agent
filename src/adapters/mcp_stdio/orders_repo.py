from __future__ import annotations

from pathlib import Path
from typing import Any

from src.adapters.mcp_stdio.client import MCPStdioClient
from src.adapters.mcp_stdio.process import MCPStdioConfig
from src.ports.orders import OrdersPort


class MCPOrdersRepo(OrdersPort):
    def __init__(self, server_path: Path, env: dict[str, str] | None = None, keep_alive: bool = True) -> None:
        cfg = MCPStdioConfig(server_path=server_path, env=env, keep_alive=keep_alive)
        self._client = MCPStdioClient(cfg)

    async def create_order(self, product_id: int, quantity: int) -> dict[str, Any]:
        return await self._client.call_tool("create_order", {"product_id": product_id, "quantity": quantity})

    async def list_orders(self) -> list[dict[str, Any]]:
        return await self._client.call_tool("list_orders", {})

    async def get_order(self, order_id: int) -> dict[str, Any]:
        return await self._client.call_tool("get_order", {"order_id": order_id})

    async def get_orders_statistics(self) -> dict[str, Any]:
        return await self._client.call_tool("get_orders_statistics", {})
