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
async def test_mcp_stdio_products_tools(tmp_path: Path):
    data_path = tmp_path / "products.json"
    data_path.write_text("[]", encoding="utf-8")

    server_path = Path("src/entrypoints/mcp_products_server/server.py").resolve()
    project_root = Path.cwd().resolve()

    env = {
        "PRODUCTS_JSON_PATH": str(data_path),
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
        assert {"list_products", "get_product", "add_product", "get_statistics"} <= tool_names

        products = _unwrap(await client.call_tool("list_products", {}))
        assert products == []

        added = _unwrap(
            await client.call_tool(
                "add_product",
                {"name": "Мышка", "price": 1500, "category": "Электроника", "in_stock": True},
            )
        )
        assert added["id"] == 1
        assert added["name"] == "Мышка"

        stats = _unwrap(await client.call_tool("get_statistics", {}))
        assert stats["count"] == 1
        assert stats["average_price"] == 1500

        got = _unwrap(await client.call_tool("get_product", {"product_id": 1}))
        assert got["name"] == "Мышка"

        with pytest.raises(Exception) as e:
            await client.call_tool("get_product", {"product_id": 999})
        assert "not found" in str(e.value).lower()
