import pytest
from httpx import AsyncClient

from src.entrypoints.api.main import app


@pytest.mark.asyncio
async def test_api_agent_query_help():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/v1/agent/query", json={"query": "что ты умеешь?"})
        assert resp.status_code == 200
        data = resp.json()
        assert "Я умею" in data["answer"]
