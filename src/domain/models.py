from __future__ import annotations

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product entity."""

    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    category: str = Field(..., min_length=1)
    in_stock: bool = True


class Statistics(BaseModel):
    """Aggregated statistics for products."""

    count: int = Field(..., ge=0)
    average_price: float = Field(..., ge=0)
