from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from src.domain.models import Product, Statistics
from src.ports.products import ProductsPort


class MCPProductsRepo(ProductsPort):
    """
    Products repository implemented via MCP STDIO calls.

    It launches MCP server as a subprocess (stdio transport) and calls tools.
    """

    def __init__(self, server_path: Path, env: dict[str, str] | None = None) -> None:
        self._lock = asyncio.Lock()
        transport = StdioTransport(
            command="python",
            args=[str(server_path)],
            env=env or {},
            cwd=str(server_path.parent),
            keep_alive=True,
        )
        self._client = Client(transport)

    async def _call(self, tool_name: str, args: dict[str, Any]) -> Any:
        async with self._lock:
            async with self._client:
                return await self._client.call_tool(tool_name, args)

    async def list_products(self) -> list[Product]:
        result = await self._call("list_products", {})
        return [Product.model_validate(x) for x in result]

    async def get_product(self, product_id: int) -> Product:
        result = await self._call("get_product", {"product_id": product_id})
        return Product.model_validate(result)

    async def add_product(self, name: str, price: float, category: str, in_stock: bool = True) -> Product:
        result = await self._call(
            "add_product",
            {"name": name, "price": price, "category": category, "in_stock": in_stock},
        )
        return Product.model_validate(result)

    async def get_statistics(self) -> Statistics:
        result = await self._call("get_statistics", {})
        return Statistics.model_validate(result)
