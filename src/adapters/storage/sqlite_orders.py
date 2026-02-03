from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SQLiteOrdersStorage:
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
                    payload TEXT NOT NULL
                )
                """
            )

    def list_orders(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, payload FROM orders ORDER BY id"
            ).fetchall()
        result: list[dict[str, Any]] = []
        for r in rows:
            data = json.loads(r["payload"])
            if isinstance(data, dict):
                data.setdefault("id", int(r["id"]))
                result.append(data)
            else:
                result.append({"id": int(r["id"]), "payload": data})
        return result

    def get_order(self, order_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, payload FROM orders WHERE id = ?",
                (int(order_id),),
            ).fetchone()
        if row is None:
            return None
        data = json.loads(row["payload"])
        if isinstance(data, dict):
            data.setdefault("id", int(row["id"]))
            return data
        return {"id": int(row["id"]), "payload": data}

    def create_order(self, order: dict[str, Any]) -> dict[str, Any]:
        payload = dict(order)
        payload.pop("id", None)
        encoded = json.dumps(payload, ensure_ascii=False)

        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO orders (payload) VALUES (?)",
                (encoded,),
            )
            new_id = int(cur.lastrowid)

        result = dict(payload)
        result["id"] = new_id
        return result

    def get_statistics(self) -> dict[str, Any]:
        orders = self.list_orders()
        total_sum = 0.0
        count = len(orders)

        for o in orders:
            v = o.get("total_price")
            if v is None:
                v = o.get("total")
            if v is None:
                price = o.get("price")
                qty = o.get("quantity")
                if price is not None and qty is not None:
                    try:
                        v = float(price) * float(qty)
                    except Exception:
                        v = 0.0
                else:
                    v = 0.0
            try:
                total_sum += float(v)
            except Exception:
                total_sum += 0.0

        avg = (total_sum / count) if count else 0.0
        return {"count": count, "total_sum": total_sum, "avg_order_value": avg}
