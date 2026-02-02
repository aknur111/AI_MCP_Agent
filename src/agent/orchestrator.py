from __future__ import annotations

from src.adapters.llm_mock.rule_llm import RuleBasedLLM
from src.domain.formatting import format_product, format_products, format_statistics
from src.domain.pricing import apply_discount
from src.ports.products import ProductsPort
from src.agent.state import AgentState


class AgentOrchestrator:
    """Implements routing + tool execution for LangGraph nodes."""

    def __init__(self, products: ProductsPort, llm: RuleBasedLLM) -> None:
        self.products = products
        self.llm = llm

    def route(self, state: AgentState) -> dict:
        query = state["query"]
        plan = self.llm.plan(query)
        return {"intent": plan.intent, "args": plan.args}

    async def execute(self, state: AgentState) -> dict:
        intent = state.get("intent", "HELP")
        args = state.get("args", {})

        try:
            if intent == "LIST":
                products = await self.products.list_products()
                return {"answer": format_products(products)}

            if intent == "LIST_BY_CATEGORY":
                category = str(args.get("category", "")).strip()
                products = await self.products.list_products()
                filtered = [p for p in products if p.category.lower() == category.lower()]
                return {"answer": format_products(filtered)}

            if intent == "STATS":
                stats = await self.products.get_statistics()
                return {"answer": format_statistics(stats)}

            if intent == "ADD":
                p = await self.products.add_product(
                    name=str(args["name"]),
                    price=float(args["price"]),
                    category=str(args["category"]),
                    in_stock=bool(args.get("in_stock", True)),
                )
                return {"answer": f"Добавлено ✅\n{format_product(p)}"}

            if intent == "DISCOUNT":
                product_id = int(args["product_id"])
                percent = float(args["percent"])
                p = await self.products.get_product(product_id)
                new_price = apply_discount(p.price, percent)
                return {
                    "answer": (
                        f"{format_product(p)}\n"
                        f"Скидка: {percent:.2f}%\n"
                        f"Цена со скидкой: {new_price:.2f} ₽"
                    )
                }

            return self.help(state)

        except Exception as e:
            return {"error": str(e), "answer": f"Ошибка: {e}"}

    def help(self, state: AgentState) -> dict:
        return {
            "answer": (
                "Я умею:\n"
                "1) Показать продукты: «Покажи продукты» или «Покажи продукты в категории Электроника»\n"
                "2) Статистика: «Какая средняя цена продуктов?»\n"
                "3) Добавить: «Добавь новый продукт: Мышка, цена 1500, категория Электроника»\n"
                "4) Скидка: «Посчитай скидку 15% на товар с ID 1»"
            )
        }
