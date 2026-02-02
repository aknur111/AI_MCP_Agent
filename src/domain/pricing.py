from __future__ import annotations


def apply_discount(price: float, percent: float) -> float:
    """Return discounted price by percent (0..100)."""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100.0), 2)
