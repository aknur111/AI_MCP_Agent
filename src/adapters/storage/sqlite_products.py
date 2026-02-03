from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class SQLiteProductsStorage:
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

    def list_products(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, price, category, in_stock FROM products ORDER BY id"
            ).fetchall()
        return [
            {
                "id": int(r["id"]),
                "name": str(r["name"]),
                "price": float(r["price"]),
                "category": str(r["category"]),
                "in_stock": bool(r["in_stock"]),
            }
            for r in rows
        ]

    def get_product(self, product_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, price, category, in_stock FROM products WHERE id = ?",
                (int(product_id),),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": int(row["id"]),
            "name": str(row["name"]),
            "price": float(row["price"]),
            "category": str(row["category"]),
            "in_stock": bool(row["in_stock"]),
        }

    def add_product(self, product: dict[str, Any]) -> dict[str, Any]:
        name = str(product.get("name", "")).strip()
        price = float(product.get("price", 0.0))
        category = str(product.get("category", "")).strip()
        in_stock = 1 if bool(product.get("in_stock", True)) else 0

        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO products (name, price, category, in_stock) VALUES (?, ?, ?, ?)",
                (name, price, category, in_stock),
            )
            new_id = int(cur.lastrowid)

        return {
            "id": new_id,
            "name": name,
            "price": price,
            "category": category,
            "in_stock": bool(in_stock),
        }

    def get_statistics(self) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt, AVG(price) AS avg_price FROM products"
            ).fetchone()
        cnt = int(row["cnt"] or 0)
        avg_price = float(row["avg_price"] or 0.0)
        return {"count": cnt, "avg_price": avg_price}
