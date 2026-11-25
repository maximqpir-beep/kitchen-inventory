"""Форматирование целого количества копеек для интерфейса."""

from django import template

register = template.Library()


@register.filter
def money(cents: int) -> str:
    """Не использовать float для денежных величин."""
    return f"{cents // 100:,}.{cents % 100:02d}".replace(",", " ")
