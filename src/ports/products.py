from __future__ import annotations

from typing import Protocol

from src.domain.models import Product, Statistics


class ProductsPort(Protocol):
    """Port (interface) for product operations."""

    async def list_products(self) -> list[Product]:
        """List all products."""

    async def get_product(self, product_id: int) -> Product:
        """Get product by ID. Raise ValueError if not found."""

    async def add_product(self, name: str, price: float, category: str, in_stock: bool = True) -> Product:
        """Create a new product and return it."""

    async def get_statistics(self) -> Statistics:
        """Get count and average price for all products."""
