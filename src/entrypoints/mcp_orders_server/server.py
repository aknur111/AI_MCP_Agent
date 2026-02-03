from __future__ import annotations

import os
import json
import sys
import sqlite3
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.domain.models import Product

mcp = FastMCP(name="Orders MCP Server")


class _SQLiteOrders:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    in_stock INTEGER NOT NULL
                )
                """
            )

    def list(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, product_id, quantity, status FROM orders ORDER BY id"
            ).fetchall()
        return [
            {
                "id": int(r["id"]),
                "product_id": int(r["product_id"]),
                "quantity": int(r["quantity"]),
                "status": str(r["status"]),
            }
            for r in rows
        ]

    def get(self, order_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            r = conn.execute(
                "SELECT id, product_id, quantity, status FROM orders WHERE id = ?",
                (int(order_id),),
            ).fetchone()
        if r is None:
            return None
        return {
            "id": int(r["id"]),
            "product_id": int(r["product_id"]),
            "quantity": int(r["quantity"]),
            "status": str(r["status"]),
        }

    def create(self, product_id: int, quantity: int) -> dict[str, Any]:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO orders (product_id, quantity, status) VALUES (?, ?, ?)",
                (int(product_id), int(quantity), "created"),
            )
            new_id = int(cur.lastrowid)
        return {"id": new_id, "product_id": int(product_id), "quantity": int(quantity), "status": "created"}

    def stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            r = conn.execute(
                "SELECT COUNT(*) AS cnt, COALESCE(SUM(quantity), 0) AS total_quantity FROM orders"
            ).fetchone()
        return {"count": int(r["cnt"] or 0), "total_quantity": int(r["total_quantity"] or 0)}

    def product_exists(self, product_id: int) -> bool:
        with self._connect() as conn:
            r = conn.execute(
                "SELECT 1 FROM products WHERE id = ? LIMIT 1",
                (int(product_id),),
            ).fetchone()
        return r is not None


def _orders_path() -> Path:
    default_path = Path(__file__).parent / "data" / "orders.json"
    return Path(os.getenv("ORDERS_JSON_PATH", str(default_path)))


def _products_path() -> Path:
    default_path = Path(__file__).parents[1] / "mcp_products_server" / "data" / "products.json"
    return Path(os.getenv("PRODUCTS_JSON_PATH", str(default_path)))


def _db_path() -> Path | None:
    v = os.getenv("DB_PATH")
    if not v:
        return None
    return Path(v)


def _use_sqlite() -> bool:
    return _db_path() is not None


def _sqlite() -> _SQLiteOrders:
    db = _db_path()
    if db is None:
        raise RuntimeError("DB_PATH is not set")
    return _SQLiteOrders(db)


def _load_json(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _product_exists_json(product_id: int) -> bool:
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
    if quantity <= 0:
        raise ValueError("quantity must be > 0")

    if _use_sqlite():
        if not _sqlite().product_exists(product_id):
            raise ValueError(f"Product with id={product_id} not found")
        return _sqlite().create(product_id=product_id, quantity=quantity)

    if not _product_exists_json(product_id):
        raise ValueError(f"Product with id={product_id} not found")

    orders_file = _orders_path()
    orders = _load_json(orders_file)
    next_id = (max([o.get("id", 0) for o in orders], default=0) + 1)
    order = {"id": next_id, "product_id": product_id, "quantity": quantity, "status": "created"}
    orders.append(order)
    _save_json(orders_file, orders)
    return order


@mcp.tool
def list_orders() -> list[dict[str, Any]]:
    if _use_sqlite():
        return _sqlite().list()
    return _load_json(_orders_path())


@mcp.tool
def get_order(order_id: int) -> dict[str, Any]:
    if _use_sqlite():
        o = _sqlite().get(order_id)
        if o is None:
            raise ValueError(f"Order with id={order_id} not found")
        return o

    orders = _load_json(_orders_path())
    for o in orders:
        if int(o.get("id", -1)) == order_id:
            return o
    raise ValueError(f"Order with id={order_id} not found")


@mcp.tool
def get_orders_statistics() -> dict[str, Any]:
    if _use_sqlite():
        return _sqlite().stats()

    orders = _load_json(_orders_path())
    count = len(orders)
    total_quantity = sum(int(o.get("quantity", 0)) for o in orders)
    return {"count": count, "total_quantity": total_quantity}


if __name__ == "__main__":
    mcp.run()
