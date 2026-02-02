from __future__ import annotations

from typing import Protocol

from src.adapters.llm_mock.rule_llm import Plan


class LLMPort(Protocol):
    """Port (interface) for LLM-like routing decisions (mock in this project)."""

    def plan(self, query: str) -> Plan:
        """Create an action plan for the agent."""
