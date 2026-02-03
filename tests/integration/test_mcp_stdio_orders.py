from __future__ import annotations

from pathlib import Path
import sys

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport


def _tool_name(t) -> str:
    """fastmcp 2.x returns Tool objects (not dicts)."""
    if hasattr(t, "name"):
        return t.name
    if hasattr(t, "model_dump"):
        return t.model_dump().get("name")
    return t["name"]


def _unwrap(res):
    if hasattr(res, "structured_content") and res.structured_content and "result" in res.structured_content:
        return res.structured_content["result"]
    if hasattr(res, "data") and res.data is not None:
        return res.data
    return res


@pytest.mark.asyncio
async def test_mcp_stdio_orders_tools(tmp_path: Path):
    orders_path = tmp_path / "orders.json"
    orders_path.write_text("[]", encoding="utf-8")

    products_path = tmp_path / "products.json"
    products_path.write_text(
        """
        [
          {"id": 1, "name": "Ноутбук", "price": 50000, "category": "Электроника", "in_stock": true}
        ]
        """.strip(),
        encoding="utf-8",
    )

    server_path = Path("src/entrypoints/mcp_orders_server/server.py").resolve()
    project_root = Path.cwd().resolve()

    env = {
        "ORDERS_JSON_PATH": str(orders_path),
        "PRODUCTS_JSON_PATH": str(products_path),
        "PYTHONPATH": str(project_root),
    }

    transport = StdioTransport(
        command=sys.executable,
        args=[str(server_path)],
        env=env,
        cwd=str(project_root),
        keep_alive=False,
    )

    client = Client(transport)

    async with client:
        tools = await client.list_tools()
        tool_names = {_tool_name(t) for t in tools}
        assert {"create_order", "list_orders", "get_order", "get_orders_statistics"} <= tool_names

        orders = _unwrap(await client.call_tool("list_orders", {}))
        assert orders == []
        created = _unwrap(await client.call_tool("create_order", {"product_id": 1, "quantity": 2}))
        assert created["id"] == 1
        assert created["product_id"] == 1
        assert created["quantity"] == 2
        assert created.get("status") in (None, "created")
        orders = _unwrap(await client.call_tool("list_orders", {}))
        assert len(orders) == 1

        got = _unwrap(await client.call_tool("get_order", {"order_id": 1}))
        assert got["id"] == 1

        stats = _unwrap(await client.call_tool("get_orders_statistics", {}))
        assert stats["count"] == 1
        assert stats["total_quantity"] == 2

        with pytest.raises(Exception) as e:
            await client.call_tool("create_order", {"product_id": 1, "quantity": 0})
        assert "quantity" in str(e.value).lower()

        with pytest.raises(Exception) as e2:
            await client.call_tool("get_order", {"order_id": 999})
        assert "not found" in str(e2.value).lower()
