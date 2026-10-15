"""Продукты, дробное количество и сроки годности."""

from datetime import date, timedelta
from decimal import Decimal, InvalidOperation


def add(goods: dict, title: str, amount: str,
        expiration_date: str | None = None) -> None:
    """Добавить партию; количество хранится как Decimal."""
    title = title.strip().casefold()
    if not title:
        raise ValueError("Введите название продукта.")
    try:
        quantity = Decimal(str(amount).replace(",", "."))
    except InvalidOperation as error:
        raise ValueError("Некорректное количество.") from error
    if not quantity.is_finite() or quantity <= 0:
        raise ValueError("Количество должно быть положительным.")
    expiry = date.fromisoformat(expiration_date) if expiration_date else None
    goods.setdefault(title, []).append({
        "amount": quantity, "expiration_date": expiry,
    })


def find(goods: dict, needle: str) -> list[str]:
    """Найти названия по подстроке без учета регистра."""
    return [title for title in goods if needle.strip().casefold() in title]


def amount(goods: dict, needle: str) -> Decimal:
    """Суммарное количество найденных продуктов в одной выбранной единице."""
    return sum((batch["amount"] for title in find(goods, needle)
                for batch in goods[title]), Decimal("0"))


def expired(goods: dict, days: int = 0,
            today: date | None = None) -> list[tuple[str, Decimal]]:
    """Партии со сроком до указанного дня включительно; None не истекает."""
    if type(days) is not int or days < 0:
        raise ValueError("Число дней должно быть неотрицательным целым.")
    limit = (today or date.today()) + timedelta(days=days)
    result = []
    for title, batches in goods.items():
        total = sum((batch["amount"] for batch in batches
                     if batch["expiration_date"] is not None
                     and batch["expiration_date"] <= limit), Decimal("0"))
        if total:
            result.append((title, total))
    return result
