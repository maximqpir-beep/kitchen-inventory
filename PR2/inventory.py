"""Функции учета: коллекции словарей, поиск, расчет и перемещения."""

from copy import deepcopy
from datetime import datetime

from catalog import CATEGORIES, ROOMS, STATES
from validation import check_data, check_item


def import_data(raw: dict) -> dict:
    """Проверить и скопировать данные из файла."""
    check_data(raw)
    return deepcopy(raw)


def export_data(data: dict) -> dict:
    """Подготовить независимую копию для JSON."""
    check_data(data)
    return deepcopy(data)


def get_item(data: dict, item_id: int) -> dict:
    """Найти партию по ID."""
    for item in data["items"]:
        if item["id"] == item_id:
            return item
    raise ValueError("Предмет с таким номером не найден.")


def get_usage_status(item: dict) -> str:
    """Сохраненный сценарий проверки состояния из ПР1."""
    if item["state_id"] == 1:
        return "Разрешен к использованию"
    return f"Использование запрещено: {STATES[item['state_id']]}"


def calculate_total(item: dict) -> int:
    """Стоимость партии в копейках."""
    return item["quantity"] * item["unit_price"]


def can_move(item: dict, room_id: int) -> bool:
    """Проверить доступность перемещения всей партии."""
    return (
        type(room_id) is int and room_id in ROOMS
        and item["state_id"] == 1 and item["room_id"] != room_id
    )


def add_item(data: dict, name: str, category_id: int, quantity: int,
             unit_price: int, room_id: int, state_id: int = 1) -> dict:
    """Добавить новую самостоятельную партию с уникальным ID."""
    new_id = max((item["id"] for item in data["items"]), default=0) + 1
    item = {
        "id": new_id, "name": name.strip(), "category_id": category_id,
        "quantity": quantity, "unit_price": unit_price,
        "room_id": room_id, "state_id": state_id,
    }
    check_item(item)
    data["items"].append(item)
    return item


def change_state(data: dict, item_id: int, state_id: int) -> None:
    """Изменить состояние; списание окончательно."""
    item = get_item(data, item_id)
    if type(state_id) is not int or state_id not in STATES:
        raise ValueError("Неизвестное состояние.")
    if item["state_id"] == 3 and state_id != 3:
        raise ValueError("Нельзя восстановить списанный предмет.")
    item["state_id"] = state_id


def move_item(data: dict, item_id: int, room_id: int) -> None:
    """Переместить всю партию и записать действие в журнал."""
    item = get_item(data, item_id)
    if not can_move(item, room_id):
        raise ValueError("Нужны исправный предмет и другое помещение.")
    move_id = max((m["id"] for m in data["moves"]), default=0) + 1
    data["moves"].append({
        "id": move_id, "item_id": item_id, "from_room": item["room_id"],
        "to_room": room_id, "created_at": datetime.now().isoformat(),
        "cancelled": False,
    })
    item["room_id"] = room_id


def cancel_move(data: dict, move_id: int) -> None:
    """Отменить последнее действующее перемещение выбранной партии."""
    move = next((m for m in data["moves"] if m["id"] == move_id), None)
    if move is None or move["cancelled"]:
        raise ValueError("Перемещение не найдено или уже отменено.")
    active = [m for m in data["moves"]
              if m["item_id"] == move["item_id"] and not m["cancelled"]]
    if active[-1] is not move:
        raise ValueError("Сначала отмените более позднее перемещение.")
    item = get_item(data, move["item_id"])
    item["room_id"] = move["from_room"]
    move["cancelled"] = True


def find_items(data: dict, query: str = "", category_id: int = 0,
               state_id: int = 0, room_id: int = 0) -> list[dict]:
    """Поиск по части названия с необязательными фильтрами."""
    return [item for item in data["items"]
            if query.strip().casefold() in item["name"].casefold()
            and (not category_id or item["category_id"] == category_id)
            and (not state_id or item["state_id"] == state_id)
            and (not room_id or item["room_id"] == room_id)]


def sort_items(items: list[dict], by: str = "name") -> list[dict]:
    """Вернуть новый отсортированный список, не меняя исходный."""
    if by == "name":
        return sorted(items, key=lambda item: item["name"].casefold())
    if by == "total":
        return sorted(items, key=calculate_total)
    raise ValueError("Неизвестный способ сортировки.")


def statistics(data: dict) -> dict:
    """Подсчитать партии, штуки, стоимость и число категорий."""
    items = data["items"]
    return {
        "batches": len(items),
        "units": sum(item["quantity"] for item in items),
        "total": sum(calculate_total(item) for item in items),
        "usable": sum(i["quantity"] for i in items if i["state_id"] == 1),
        "categories": len({item["category_id"] for item in items}),
    }


def format_item(item: dict) -> str:
    """Строка карточки для консольного интерфейса."""
    total = calculate_total(item)
    return (
        f"{item['id']} — {item['name']} | {CATEGORIES[item['category_id']]}"
        f" | {STATES[item['state_id']]} | {ROOMS[item['room_id']]}"
        f" | {item['quantity']} шт. | {total // 100}.{total % 100:02d} руб."
    )
