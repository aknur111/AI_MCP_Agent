from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from fastmcp import Client

from src.adapters.mcp_stdio.process import MCPStdioConfig
from src.domain.models import Product, Statistics
from src.ports.products import ProductsPort


def _unwrap(result: Any) -> Any:
    sc = getattr(result, "structured_content", None)
    if isinstance(sc, dict):
        if "result" in sc:
            return sc["result"]
        return sc
    return result


@dataclass
class MCPProductsRepo(ProductsPort):
    server_path: Path
    keep_alive: bool = True
    cwd: Optional[Path] = None
    env: Optional[dict[str, str]] = None

    def _client(self) -> Client:
        transport = MCPStdioConfig(
            server_path=self.server_path,
            keep_alive=self.keep_alive,
            cwd=self.cwd,
            env=self.env,
        ).to_transport()
        return Client(transport)

    async def _call(self, name: str, args: dict[str, Any]) -> Any:
        client = self._client()
        async with client:
            res = await client.call_tool(name, args)
            return _unwrap(res)

    async def list_products(self) -> list[Product]:
        result = await self._call("list_products", {})
        return [Product.model_validate(x) for x in (result or [])]

    async def get_product(self, product_id: int) -> Product:
        result = await self._call("get_product", {"product_id": product_id})
        return Product.model_validate(result)

    async def add_product(
        self,
        name: str,
        price: float,
        category: str,
        in_stock: bool = True,
    ) -> Product:
        result = await self._call(
            "add_product",
            {"name": name, "price": price, "category": category, "in_stock": in_stock},
        )
        return Product.model_validate(result)

    async def get_statistics(self) -> Statistics:
        result = await self._call("get_statistics", {})
        return Statistics.model_validate(result)
