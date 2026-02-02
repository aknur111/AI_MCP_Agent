from __future__ import annotations

from fastapi import FastAPI

from src.core.config import Settings
from src.core.logging import setup_logging
from src.adapters.llm_mock.rule_llm import RuleBasedLLM
from src.adapters.mcp_stdio.products_repo import MCPProductsRepo
from src.agent.orchestrator import AgentOrchestrator
from src.agent.graph import build_graph
from src.entrypoints.api.v1.routes import router as v1_router

settings = Settings.from_env()
setup_logging(settings.log_level)

app = FastAPI(title="AI MCP Agent")

# Build agent service once (reuse stdio subprocess across requests via keep_alive).
_products_repo = MCPProductsRepo(
    server_path=settings.mcp_products_server_path,
    env={"PRODUCTS_JSON_PATH": str(settings.products_json_path)},
)
_llm = RuleBasedLLM()
_orchestrator = AgentOrchestrator(products=_products_repo, llm=_llm)
_graph = build_graph(_orchestrator)


class AgentService:
    async def run(self, query: str) -> dict:
        state = {"query": query}
        out = await _graph.ainvoke(state)
        return {"answer": out.get("answer", ""), "error": out.get("error")}


_agent_service = AgentService()


def get_agent_service() -> AgentService:
    return _agent_service


app.include_router(v1_router)
