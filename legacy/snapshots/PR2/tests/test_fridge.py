"""Проверки дополнительного примера «Холодильник»."""

from datetime import date
from decimal import Decimal

import pytest

from fridge_task.fridge import add, amount, expired, find


def test_add_find_and_fractional_amount():
    goods = {}
    add(goods, "Молоко", "1.5", "2026-10-02")
    add(goods, "молоко", "0,25")
    assert find(goods, "МОЛ") == ["молоко"]
    assert amount(goods, "молоко") == Decimal("1.75")


def test_expiration_boundary():
    goods = {}
    add(goods, "Молоко", "1.5", "2026-09-30")
    add(goods, "Молоко", "1", "2026-10-02")
    add(goods, "Соль", "1")
    assert expired(goods, today=date(2026, 9, 30)) == [
        ("молоко", Decimal("1.5")),
    ]
    assert expired(goods, 2, date(2026, 9, 30)) == [
        ("молоко", Decimal("2.5")),
    ]


@pytest.mark.parametrize("quantity", ["0", "-1", "abc", "NaN"])
def test_invalid_quantity(quantity):
    with pytest.raises(ValueError):
        add({}, "Продукт", quantity)


def test_invalid_date():
    with pytest.raises(ValueError):
        add({}, "Продукт", "1", "2026-02-30")
