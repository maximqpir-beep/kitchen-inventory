"""Ввод чисел, денежных сумм и вариантов меню."""

from decimal import Decimal, InvalidOperation


def input_int(prompt: str, minimum: int = 1) -> int:
    """Повторять вопрос, пока не введено допустимое целое число."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Введите целое число не меньше {minimum}.")


def choose(options: dict[int, str], title: str) -> int:
    """Показать варианты и вернуть существующий номер."""
    print(title)
    for number, name in options.items():
        print(f"{number} — {name}")
    while True:
        value = input_int("Ваш выбор: ", min(options))
        if value in options:
            return value
        print("Такого варианта нет.")


def input_price() -> int:
    """Принять рубли, вернуть копейки без округления лишних знаков."""
    while True:
        try:
            text = input("Цена за штуку, руб.: ").strip().replace(",", ".")
            value = Decimal(text)
            if not value.is_finite() or value <= 0:
                raise ValueError
            cents = value * 100
            if cents != cents.to_integral_value():
                raise ValueError
            return int(cents)
        except (InvalidOperation, ValueError, OverflowError):
            print("Нужна положительная цена, например 1250.50.")
