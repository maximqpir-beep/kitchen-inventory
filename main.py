"""Числовое меню системы учета кухонного инвентаря."""

import argparse
from copy import deepcopy
from pathlib import Path

from catalog import CATEGORIES, ROOMS, STATES
from inventory import (
    add_item, cancel_move, change_state, export_data, find_items,
    format_item, get_item, get_usage_status, move_item, sort_items,
    statistics,
)
from storage import DEFAULT_PATH, load_data, save_data
from utils import choose, input_int, input_price

MENU = {
    1: "Список предметов", 2: "Добавить партию", 3: "Поиск и фильтры",
    4: "Сортировка", 5: "Переместить партию", 6: "Изменить состояние",
    7: "Статистика", 8: "История перемещений",
    9: "Отменить перемещение", 10: "Проверить пригодность", 0: "Выход",
}


def show_items(items: list) -> None:
    """Вывести все найденные партии с ID для выбора."""
    if not items:
        print("Предметы не найдены.")
    for item in items:
        print(format_item(item))


def select_item(data: dict) -> int:
    """Показать список и запросить существующий ID."""
    show_items(find_items(data))
    item_id = input_int("Номер предмета: ")
    get_item(data, item_id)
    return item_id


def show_history(data: dict) -> None:
    """Показать номера перемещений, в том числе отмененных."""
    moves = export_data(data)["moves"]
    if not moves:
        print("История пуста.")
    for move in moves:
        status = "отменено" if move["cancelled"] else "выполнено"
        print(
            f"{move['id']} — предмет {move['item_id']} | "
            f"{ROOMS[move['from_room']]} -> {ROOMS[move['to_room']]} | "
            f"{move['created_at']} | {status}"
        )


def handle_action(data: dict, action: int) -> bool:
    """Выполнить действие; вернуть True, если данные изменились."""
    if action == 1:
        show_items(find_items(data))
    elif action == 2:
        name = input("Название предмета: ").strip()
        category = choose(CATEGORIES, "Категория:")
        quantity = input_int("Количество: ")
        price = input_price()
        room = choose(ROOMS, "Помещение:")
        state = choose(STATES, "Состояние:")
        add_item(data, name, category, quantity, price, room, state)
        return True
    elif action == 3:
        query = input("Часть названия (Enter — любое): ")
        category = choose({0: "Все", **CATEGORIES}, "Категория:")
        state = choose({0: "Все", **STATES}, "Состояние:")
        room = choose({0: "Все", **ROOMS}, "Помещение:")
        show_items(find_items(data, query, category, state, room))
    elif action == 4:
        option = choose({1: "По названию", 2: "По стоимости"}, "Порядок:")
        key = "name" if option == 1 else "total"
        show_items(sort_items(find_items(data), key))
    elif action == 5:
        item_id = select_item(data)
        room = choose(ROOMS, "Куда переместить всю партию?")
        move_item(data, item_id, room)
        return True
    elif action == 6:
        item_id = select_item(data)
        state = choose(STATES, "Новое состояние:")
        change_state(data, item_id, state)
        return True
    elif action == 7:
        result = statistics(data)
        total = result["total"]
        print(f"Партий: {result['batches']}; предметов: {result['units']}")
        print(f"Исправных предметов: {result['usable']}")
        print(f"Категорий: {result['categories']}")
        print(f"Стоимость всех партий: {total // 100}.{total % 100:02d}")
    elif action == 8:
        show_history(data)
    elif action == 9:
        show_history(data)
        cancel_move(data, input_int("Номер отменяемого перемещения: "))
        return True
    elif action == 10:
        print(get_usage_status(get_item(data, select_item(data))))
    return False


def main() -> None:
    """Загрузить данные и сохранять после каждого успешного изменения."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_PATH)
    path = parser.parse_args().data
    try:
        data = load_data(path)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"Не удалось открыть данные: {error}")
        print("Файл не изменен. Проверьте путь и содержимое JSON.")
        return
    print("Система учета кухонного инвентаря | ЭФБО-12-24")
    try:
        while True:
            action = choose(MENU, "\nГлавное меню:")
            if action == 0:
                print("Программа завершена. Все изменения сохранены.")
                break
            try:
                candidate = deepcopy(data)
                if handle_action(candidate, action):
                    save_data(candidate, path)
                    data = candidate
                    print("Готово. Изменения сохранены.")
            except (OSError, ValueError, UnicodeError) as error:
                print(f"Операция отклонена: {error}")
            input("\nEnter — вернуться в меню...")
    except (EOFError, KeyboardInterrupt):
        print("\nВыход. Незавершенная операция не сохранена.")


if __name__ == "__main__":
    main()
