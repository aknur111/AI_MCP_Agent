from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal, Optional


Intent = Literal["LIST", "LIST_BY_CATEGORY", "STATS", "ADD", "DISCOUNT", "HELP"]


@dataclass(frozen=True)
class Plan:
    """Routing result produced by a mock LLM."""

    intent: Intent
    args: dict[str, Any]


class RuleBasedLLM:
    """
    A tiny "mock LLM" that routes Russian user queries into structured intents + args.

    This replaces real model calls (no API keys required).
    """

    _re_add = re.compile(
        r"добав(ь|ить)\s+нов(ый|ую)\s+продукт:\s*(?P<name>[^,]+),\s*цена\s*(?P<price>[\d]+(?:\.[\d]+)?),\s*категори[яи]\s*(?P<category>.+)",
        re.IGNORECASE,
    )
    _re_discount = re.compile(
        r"скидк[ау]\s*(?P<percent>[\d]+(?:\.[\d]+)?)\s*%.*?\b(id|ID)\s*(?P<id>\d+)",
        re.IGNORECASE,
    )
    _re_category = re.compile(r"категори[яи]\s+(?P<category>.+)", re.IGNORECASE)

    def plan(self, query: str) -> Plan:
        q = query.strip()

        if not q:
            return Plan(intent="HELP", args={})

        if "средняя цена" in q.lower() or "статистик" in q.lower():
            return Plan(intent="STATS", args={})

        m_add = self._re_add.search(q)
        if m_add:
            name = m_add.group("name").strip()
            price = float(m_add.group("price"))
            category = m_add.group("category").strip()
            return Plan(intent="ADD", args={"name": name, "price": price, "category": category, "in_stock": True})

        m_disc = self._re_discount.search(q)
        if m_disc:
            percent = float(m_disc.group("percent"))
            product_id = int(m_disc.group("id"))
            return Plan(intent="DISCOUNT", args={"percent": percent, "product_id": product_id})

        if q.lower().startswith("покажи") or "покажи" in q.lower() or "список" in q.lower():
            m_cat = self._re_category.search(q)
            if m_cat:
                category = m_cat.group("category").strip()
                return Plan(intent="LIST_BY_CATEGORY", args={"category": category})
            return Plan(intent="LIST", args={})

        return Plan(intent="HELP", args={"hint": "Я понимаю: список, статистика, добавление, скидка."})
