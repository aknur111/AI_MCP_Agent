from __future__ import annotations

from src.adapters.llm_mock.rule_llm import RuleBasedLLM
from src.domain.formatting import format_product, format_products, format_statistics
from src.domain.pricing import apply_discount
from src.ports.products import ProductsPort
from src.ports.orders import OrdersPort
from src.agent.state import AgentState


class AgentOrchestrator:
    def __init__(self, products: ProductsPort, orders: OrdersPort, llm: RuleBasedLLM) -> None:
        self.products = products
        self.orders = orders
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
                return {"answer": f"Добавлено\n{format_product(p)}"}

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

            if intent == "ORDER_CREATE":
                created = await self.orders.create_order(
                    product_id=int(args["product_id"]),
                    quantity=int(args["quantity"]),
                )
                return {"answer": f"Заказ создан\n{created}"}

            if intent == "ORDER_LIST":
                orders = await self.orders.list_orders()
                if not orders:
                    return {"answer": "Заказов пока нет."}
                lines = ["ID | product_id | qty | status", "---|---:|---:|---"]
                for o in orders:
                    lines.append(f'{o.get("id")} | {o.get("product_id")} | {o.get("quantity")} | {o.get("status")}')
                return {"answer": "\n".join(lines)}

            if intent == "ORDER_GET":
                order_id = int(args["order_id"])
                order = await self.orders.get_order(order_id)
                return {"answer": f"Заказ #{order_id}:\n{order}"}

            if intent == "ORDER_STATS":
                stats = await self.orders.get_orders_statistics()
                return {"answer": f"Статистика заказов:\n{stats}"}

            return self.help(state)

        except Exception as e:
            return {"error": str(e), "answer": f"Ошибка: {e}"}

    def help(self, state: AgentState) -> dict:
        return {
            "answer": (
                "Я умею:\n"
                "— Продукты:\n"
                "  1) «Покажи продукты» / «Покажи продукты в категории Электроника»\n"
                "  2) «Какая средняя цена продуктов?»\n"
                "  3) «Добавь новый продукт: Мышка, цена 1500, категория Электроника»\n"
                "  4) «Посчитай скидку 15% на товар с ID 1»\n"
                "— Заказы:\n"
                "  5) «Создай заказ: продукт 1, количество 2»\n"
                "  6) «Покажи заказы»\n"
                "  7) «Статистика заказов»\n"
                "  8) «Покажи заказ 1»"
            )
        }
