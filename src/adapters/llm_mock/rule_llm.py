from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

Intent = Literal[
    "LIST",
    "LIST_BY_CATEGORY",
    "STATS",
    "ADD",
    "DISCOUNT",
    "ORDER_CREATE",
    "ORDER_LIST",
    "ORDER_GET",
    "ORDER_STATS",
    "HELP",
]


@dataclass(frozen=True)
class Plan:
    intent: Intent
    args: dict[str, Any]


class RuleBasedLLM:
    _re_add = re.compile(
        r"добав(ь|ить)\s+нов(ый|ую)\s+продукт:\s*(?P<name>[^,]+),\s*цена\s*(?P<price>[\d]+(?:\.[\d]+)?),\s*категори[яи]\s*(?P<category>.+)",
        re.IGNORECASE,
    )
    _re_discount = re.compile(
        r"скидк[ау]\s*(?P<percent>[\d]+(?:\.[\d]+)?)\s*%.*?\b(id|ID)\s*(?P<id>\d+)",
        re.IGNORECASE,
    )
    _re_category = re.compile(r"категори[яи]\s+(?P<category>.+)", re.IGNORECASE)

    _re_order_create = re.compile(
        r"(созда(й|ть)\s+заказ|оформ(и|ить)\s+заказ)\s*[:\-]?\s*(продукт|товар)\s*(?P<pid>\d+)\s*,?\s*(количеств(о|а))\s*(?P<qty>\d+)",
        re.IGNORECASE,
    )
    _re_order_get = re.compile(r"(заказ)\s*(id|ID)?\s*(?P<oid>\d+)", re.IGNORECASE)

    def plan(self, query: str) -> Plan:
        q = query.strip()
        if not q:
            return Plan(intent="HELP", args={})

        ql = q.lower()

        if "статист" in ql and "заказ" in ql:
            return Plan(intent="ORDER_STATS", args={})

        if "покажи" in ql and "заказ" in ql:
            return Plan(intent="ORDER_LIST", args={})

        m_order_create = self._re_order_create.search(q)
        if m_order_create:
            return Plan(
                intent="ORDER_CREATE",
                args={"product_id": int(m_order_create.group("pid")), "quantity": int(m_order_create.group("qty"))},
            )

        if "заказ" in ql and ("покажи" in ql or "найди" in ql or "получ" in ql):
            m_order_get = self._re_order_get.search(q)
            if m_order_get:
                return Plan(intent="ORDER_GET", args={"order_id": int(m_order_get.group("oid"))})

        if "средняя цена" in ql or "статистик" in ql:
            return Plan(intent="STATS", args={})

        m_add = self._re_add.search(q)
        if m_add:
            return Plan(
                intent="ADD",
                args={
                    "name": m_add.group("name").strip(),
                    "price": float(m_add.group("price")),
                    "category": m_add.group("category").strip(),
                    "in_stock": True,
                },
            )

        m_disc = self._re_discount.search(q)
        if m_disc:
            return Plan(intent="DISCOUNT", args={"percent": float(m_disc.group("percent")), "product_id": int(m_disc.group("id"))})

        if ql.startswith("покажи") or "покажи" in ql or "список" in ql:
            m_cat = self._re_category.search(q)
            if m_cat:
                return Plan(intent="LIST_BY_CATEGORY", args={"category": m_cat.group("category").strip()})
            return Plan(intent="LIST", args={})

        return Plan(intent="HELP", args={"hint": "Я понимаю: продукты (список/статистика/добавить/скидка) и заказы (создать/показать/статистика)."})
