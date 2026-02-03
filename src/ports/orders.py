from __future__ import annotations

from typing import Protocol, Any


class OrdersPort(Protocol):
    async def create_order(self, product_id: int, quantity: int) -> dict[str, Any]:
        """
        Create an order.

        Args:
            product_id: ID of the product to order
            quantity: quantity (> 0)

        Returns:
            Created order as a JSON-like dict.
        """

    async def list_orders(self) -> list[dict[str, Any]]:
        """Return all orders."""

    async def get_order(self, order_id: int) -> dict[str, Any]:
        """
        Get order by ID.

        Raises:
            ValueError: if order not found
        """

    async def get_orders_statistics(self) -> dict[str, Any]:
        """Return order statistics (count, totals, etc.)."""
