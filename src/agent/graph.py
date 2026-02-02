from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from src.agent.state import AgentState
from src.agent.orchestrator import AgentOrchestrator


def build_graph(orchestrator: AgentOrchestrator):
    """
    Build a small LangGraph workflow:

    START -> route -> (execute | help) -> END
    """
    g = StateGraph(AgentState)

    g.add_node("route", orchestrator.route)
    g.add_node("execute", orchestrator.execute)
    g.add_node("help", orchestrator.help)

    g.add_edge(START, "route")

    def choose_next(state: AgentState) -> str:
        intent = state.get("intent", "HELP")
        if intent in {"LIST", "LIST_BY_CATEGORY", "STATS", "ADD", "DISCOUNT"}:
            return "execute"
        return "help"

    g.add_conditional_edges("route", choose_next, {"execute": "execute", "help": "help"})
    g.add_edge("execute", END)
    g.add_edge("help", END)

    return g.compile()
