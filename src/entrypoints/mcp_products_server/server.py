from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from src.adapters.storage.json_products import JsonProductsStorage
from src.domain.models import Product, Statistics

mcp = FastMCP(name="Products MCP Server")


def _get_storage() -> JsonProductsStorage:
    path = Path(os.getenv("PRODUCTS_JSON_PATH", str(Path(__file__).parent / "data/products.json")))
    return JsonProductsStorage(path)


@mcp.tool
def list_products() -> list[dict[str, Any]]:
    storage = _get_storage()
    products = storage.load()
    return [p.model_dump() for p in products]


@mcp.tool
def get_product(product_id: int) -> dict[str, Any]:
    storage = _get_storage()
    products = storage.load()
    for p in products:
        if p.id == product_id:
            return p.model_dump()
    raise ValueError(f"Product with id={product_id} not found")


@mcp.tool
def add_product(name: str, price: float, category: str, in_stock: bool = True) -> dict[str, Any]:
    storage = _get_storage()
    products = storage.load()
    next_id = (max([p.id for p in products], default=0) + 1)
    p = Product(id=next_id, name=name.strip(), price=float(price), category=category.strip(), in_stock=bool(in_stock))
    products.append(p)
    storage.save(products)
    return p.model_dump()


@mcp.tool
def get_statistics() -> dict[str, Any]:
    storage = _get_storage()
    products = storage.load()
    count = len(products)
    avg = round(sum(p.price for p in products) / count, 2) if count else 0.0
    stats = Statistics(count=count, average_price=avg)
    return stats.model_dump()


if __name__ == "__main__":
    mcp.run()
