import pytest
from src.domain.pricing import apply_discount


def test_apply_discount_ok():
    assert apply_discount(100.0, 15) == 85.0


def test_apply_discount_bounds():
    with pytest.raises(ValueError):
        apply_discount(100.0, -1)
    with pytest.raises(ValueError):
        apply_discount(100.0, 101)
