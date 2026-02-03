from __future__ import annotations

import os
import sys
import sqlite3
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.adapters.storage.json_products import JsonProductsStorage
from src.domain.models import Product, Statistics

mcp = FastMCP(name="Products MCP Server")


class _SQLiteProducts:
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
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    in_stock INTEGER NOT NULL
                )
                """
            )

    def list(self) -> list[Product]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, price, category, in_stock FROM products ORDER BY id"
            ).fetchall()
        return [
            Product(
                id=int(r["id"]),
                name=str(r["name"]),
                price=float(r["price"]),
                category=str(r["category"]),
                in_stock=bool(r["in_stock"]),
            )
            for r in rows
        ]

    def get(self, product_id: int) -> Product | None:
        with self._connect() as conn:
            r = conn.execute(
                "SELECT id, name, price, category, in_stock FROM products WHERE id = ?",
                (int(product_id),),
            ).fetchone()
        if r is None:
            return None
        return Product(
            id=int(r["id"]),
            name=str(r["name"]),
            price=float(r["price"]),
            category=str(r["category"]),
            in_stock=bool(r["in_stock"]),
        )

    def add(self, name: str, price: float, category: str, in_stock: bool) -> Product:
        name = name.strip()
        category = category.strip()
        price = float(price)
        in_stock_i = 1 if bool(in_stock) else 0

        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO products (name, price, category, in_stock) VALUES (?, ?, ?, ?)",
                (name, price, category, in_stock_i),
            )
            new_id = int(cur.lastrowid)

        return Product(
            id=new_id,
            name=name,
            price=price,
            category=category,
            in_stock=bool(in_stock_i),
        )

    def stats(self) -> Statistics:
        with self._connect() as conn:
            r = conn.execute(
                "SELECT COUNT(*) AS cnt, AVG(price) AS avg_price FROM products"
            ).fetchone()
        cnt = int(r["cnt"] or 0)
        avg = float(r["avg_price"] or 0.0)
        avg = round(avg, 2)
        return Statistics(count=cnt, average_price=avg)


def _json_path() -> Path:
    default_path = Path(__file__).parent / "data" / "products.json"
    return Path(os.getenv("PRODUCTS_JSON_PATH", str(default_path)))


def _db_path() -> Path | None:
    v = os.getenv("DB_PATH")
    if not v:
        return None
    return Path(v)


def _use_sqlite() -> bool:
    return _db_path() is not None


def _sqlite() -> _SQLiteProducts:
    db = _db_path()
    if db is None:
        raise RuntimeError("DB_PATH is not set")
    return _SQLiteProducts(db)


def _json_storage() -> JsonProductsStorage:
    return JsonProductsStorage(_json_path())


@mcp.tool
def list_products() -> list[dict[str, Any]]:
    if _use_sqlite():
        products = _sqlite().list()
    else:
        products = _json_storage().load()
    return [p.model_dump() for p in products]


@mcp.tool
def get_product(product_id: int) -> dict[str, Any]:
    if _use_sqlite():
        p = _sqlite().get(product_id)
        if p is None:
            raise ValueError(f"Product with id={product_id} not found")
        return p.model_dump()

    products = _json_storage().load()
    for p in products:
        if p.id == product_id:
            return p.model_dump()
    raise ValueError(f"Product with id={product_id} not found")


@mcp.tool
def add_product(name: str, price: float, category: str, in_stock: bool = True) -> dict[str, Any]:
    if _use_sqlite():
        p = _sqlite().add(name=name, price=price, category=category, in_stock=in_stock)
        return p.model_dump()

    storage = _json_storage()
    products = storage.load()
    next_id = (max([p.id for p in products], default=0) + 1)
    p = Product(
        id=next_id,
        name=name.strip(),
        price=float(price),
        category=category.strip(),
        in_stock=bool(in_stock),
    )
    products.append(p)
    storage.save(products)
    return p.model_dump()


@mcp.tool
def get_statistics() -> dict[str, Any]:
    if _use_sqlite():
        stats = _sqlite().stats()
        return stats.model_dump()

    products = _json_storage().load()
    count = len(products)
    avg = round(sum(p.price for p in products) / count, 2) if count else 0.0
    stats = Statistics(count=count, average_price=avg)
    return stats.model_dump()


if __name__ == "__main__":
    mcp.run()
