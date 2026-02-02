from __future__ import annotations

from typing import Iterable

from src.domain.models import Product, Statistics


def format_products(products: Iterable[Product]) -> str:
    """Human-friendly formatting for a product list."""
    items = list(products)
    if not items:
        return "Ничего не найдено."

    lines = ["ID | Название | Цена | Категория | В наличии", "---|---|---:|---|---"]
    for p in items:
        stock = "да" if p.in_stock else "нет"
        lines.append(f"{p.id} | {p.name} | {p.price:.2f} | {p.category} | {stock}")
    return "\n".join(lines)


def format_product(p: Product) -> str:
    """Human-friendly formatting for a single product."""
    stock = "да" if p.in_stock else "нет"
    return f"Товар #{p.id}: {p.name} — {p.price:.2f} ₽, категория: {p.category}, в наличии: {stock}"


def format_statistics(stats: Statistics) -> str:
    """Human-friendly formatting for statistics."""
    return f"Количество товаров: {stats.count}\nСредняя цена: {stats.average_price:.2f} ₽"
