"""Проверка числовых меню: python test_menu.py."""
from pathlib import Path
import subprocess
import sys

PROGRAM = Path(__file__).with_name("main.py")
ITEMS = [
    ("Кастрюля 5 л", "2501.00"),
    ("Нож поварской", "1700.00"),
    ("Сковорода", "3600.00"),
    ("Доска разделочная", "900.00"),
    ("Половник", "640.00"),
    ("Венчик", "560.00"),
    ("Дуршлаг", "1300.00"),
    ("Противень", "1900.00"),
]


def test_numbered_menus():
    cases = []
    for number, (name, cost) in enumerate(ITEMS, 1):
        cases.append((
            f"Предмет {number}", f"{number}\n2\n1\n3\n",
            f"Предмет: {name};", f"Стоимость партии: {cost} руб.",
        ))
    cases.extend([
        ("Неверный предмет", "9\n", "Ошибка:", "от 1 до 8"),
        ("Пустой выбор", "\n", "Ошибка:", "от 1 до 8"),
        ("Неверное состояние", "1\n1\n4\n", "Ошибка:", "от 1 до 3"),
        ("Неверное помещение", "1\n1\n1\n5\n", "Ошибка:", "от 1 до 4"),
        ("Ремонт", "2\n1\n2\n3\n", "Использование запрещено",
         "Текущее помещение: Горячий цех"),
        ("Списание", "2\n1\n3\n3\n", "Использование запрещено",
         "Текущее помещение: Горячий цех"),
        ("То же помещение", "1\n1\n1\n1\n", "Перемещение отклонено",
         "Текущее помещение: Горячий цех"),
        ("Ноль", "1\n0\n", "Ошибка:", "от 1 до 10000"),
        ("Текст вместо количества", "1\nabc\n", "Ошибка:", "целое число"),
        ("Превышение", "1\n10001\n", "Ошибка:", "от 1 до 10000"),
        ("Верхняя граница", "1\n10000\n1\n4\n", "12505000.00 руб.",
         "Текущее помещение: Моечная"),
    ])
    for label, data, first, second in cases:
        result = subprocess.run(
            [sys.executable, str(PROGRAM)], input=data, text=True,
            capture_output=True, check=True,
        )
        assert first in result.stdout, (label, result.stdout)
        assert second in result.stdout, (label, result.stdout)
        if label.startswith("Предмет "):
            assert "Текущее помещение: Склад" in result.stdout
        print(f"PASS: {label}")
    print(f"Успешно: {len(cases)} сценариев.")


if __name__ == "__main__":
    test_numbered_menus()
