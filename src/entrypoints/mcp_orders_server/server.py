from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from src.domain.models import Product  

mcp = FastMCP(name="Orders MCP Server")


def _orders_path() -> Path:
    default_path = Path(__file__).parent / "data" / "orders.json"
    return Path(os.getenv("ORDERS_JSON_PATH", str(default_path)))


def _products_path() -> Path:
    default_path = Path(__file__).parents[1] / "mcp_products_server" / "data" / "products.json"
    return Path(os.getenv("PRODUCTS_JSON_PATH", str(default_path)))


def _load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _product_exists(product_id: int) -> bool:
    path = _products_path()
    if not path.exists():
        return True
    raw = _load_json(path)
    for item in raw:
        try:
            p = Product.model_validate(item)
        except Exception:
            continue
        if p.id == product_id:
            return True
    return False


@mcp.tool
def create_order(product_id: int, quantity: int) -> dict[str, Any]:
    """
    Создать заказ.

    Args:
        product_id: ID продукта
        quantity: количество (должно быть > 0)

    Returns:
        dict: созданный заказ

    Raises:
        ValueError: если quantity <= 0 или продукт не найден (если включена валидация)
    """
    if quantity <= 0:
        raise ValueError("quantity must be > 0")

    if not _product_exists(product_id):
        raise ValueError(f"Product with id={product_id} not found")

    orders_file = _orders_path()
    orders = _load_json(orders_file)

    next_id = (max([o.get("id", 0) for o in orders], default=0) + 1)

    order = {
        "id": next_id,
        "product_id": product_id,
        "quantity": quantity,
        "status": "created",
    }
    orders.append(order)
    _save_json(orders_file, orders)
    return order


@mcp.tool
def list_orders() -> list[dict[str, Any]]:
    """Получить список всех заказов."""
    return _load_json(_orders_path())


@mcp.tool
def get_order(order_id: int) -> dict[str, Any]:
    """
    Получить заказ по ID.

    Raises:
        ValueError: если заказ не найден
    """
    orders = _load_json(_orders_path())
    for o in orders:
        if int(o.get("id", -1)) == order_id:
            return o
    raise ValueError(f"Order with id={order_id} not found")


@mcp.tool
def get_orders_statistics() -> dict[str, Any]:
    """
    Статистика заказов:
    - count: количество заказов
    - total_quantity: суммарное количество позиций по всем заказам
    """
    orders = _load_json(_orders_path())
    count = len(orders)
    total_quantity = sum(int(o.get("quantity", 0)) for o in orders)
    return {"count": count, "total_quantity": total_quantity}


if __name__ == "__main__":
    mcp.run()
