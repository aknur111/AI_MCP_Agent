from __future__ import annotations

from src.core.config import Settings
from src.adapters.llm_mock.rule_llm import RuleBasedLLM
from src.adapters.mcp_stdio.products_repo import MCPProductsRepo
from src.adapters.mcp_stdio.orders_repo import MCPOrdersRepo
from src.agent.orchestrator import AgentOrchestrator
from src.agent.graph import build_graph


class AgentService:
    async def run(self, query: str) -> dict:
        state = {"query": query}
        out = await self._graph.ainvoke(state)
        return {"answer": out.get("answer", ""), "error": out.get("error")}

    def __init__(self) -> None:
        settings = Settings.from_env()

        products_repo = MCPProductsRepo(
            server_path=settings.mcp_products_server_path,
            env={"PRODUCTS_JSON_PATH": str(settings.products_json_path)},
        )

        orders_repo = MCPOrdersRepo(
            server_path=settings.mcp_orders_server_path,
            env={
                "ORDERS_JSON_PATH": str(settings.orders_json_path),
                "PRODUCTS_JSON_PATH": str(settings.products_json_path),
            },
        )

        llm = RuleBasedLLM()
        orchestrator = AgentOrchestrator(products=products_repo, orders=orders_repo, llm=llm)
        self._graph = build_graph(orchestrator)

_agent_service = AgentService()


def get_agent_service() -> AgentService:
    return _agent_service
