"""Проверки правил учета; совместимы с pytest и прямым запуском."""
from main import calculate_total, can_move, get_usage_status


def test_cost():
    assert calculate_total(3, 125050) == 375150
    assert calculate_total(1, 1) == 1


def test_usage():
    assert get_usage_status("исправен") == "Разрешен к использованию"
    assert "запрещено" in get_usage_status("требует ремонта")
    assert "запрещено" in get_usage_status("списан")
    assert "запрещено" in get_usage_status("неизвестно")


def test_movement():
    assert can_move("исправен", "Горячий цех", "Склад")
    assert not can_move("требует ремонта", "Горячий цех", "Склад")
    assert not can_move("списан", "Горячий цех", "Склад")
    assert not can_move("исправен", "Горячий цех", " горячий ЦЕХ ")
    assert not can_move("исправен", "Горячий цех", "  ")


if __name__ == "__main__":
    test_cost()
    test_usage()
    test_movement()
    print("3 проверки успешно выполнены.")
