from __future__ import annotations

from typing import Protocol

from src.adapters.llm_mock.rule_llm import Plan


class LLMPort(Protocol):
    def plan(self, query: str) -> Plan:
