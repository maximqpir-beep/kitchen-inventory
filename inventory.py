"""Коллекции объектов: поиск, добавление, журнал и статистика."""

from datetime import datetime

from catalog import CATEGORIES, ROOMS, STATES
from models import Category, Condition, Item, Movement, Room
from validation import check_data


def import_data(raw: dict) -> dict:
    """Создать объекты и восстановить общие ссылки после загрузки JSON."""
    check_data(raw)
    categories = {key: Category(key, name) for key, name in CATEGORIES.items()}
    conditions = {key: Condition(key, name) for key, name in STATES.items()}
    rooms = {key: Room(key, name) for key, name in ROOMS.items()}
    items = [Item.from_dict(row, categories, conditions, rooms)
             for row in raw["items"]]
    indexed = {item.id: item for item in items}
    moves = [Movement(
        row["id"], indexed[row["item_id"]], rooms[row["from_room"]],
        rooms[row["to_room"]], row["created_at"], row["cancelled"],
    ) for row in raw["moves"]]
    return {
        "items": items, "moves": moves, "categories": categories,
        "conditions": conditions, "rooms": rooms,
    }


def export_data(data: dict) -> dict:
    """Преобразовать объекты в прежний JSON-формат ПР2."""
    raw = {
        "version": 1, "items": [item.to_dict() for item in data["items"]],
        "moves": [move.to_dict() for move in data["moves"]],
    }
    check_data(raw)
    return raw


def get_item(data: dict, item_id: int) -> Item:
    """Поиск относится к коллекции, поэтому остается функцией."""
    for item in data["items"]:
        if item.id == item_id:
            return item
    raise ValueError("Предмет с таким номером не найден.")


def get_usage_status(item: Item) -> str:
    """Адаптер сценария ПР1 к методу предмета."""
    return f"{item.usage_status()}\n{item.handling_note()}"


def calculate_total(item: Item) -> int:
    return item.total


def can_move(item: Item, room_id: int) -> bool:
    if type(room_id) is not int or room_id not in ROOMS:
        return False
    return item.can_move(Room(room_id, ROOMS[room_id]))


def add_item(data: dict, name: str, category_id: int, quantity: int,
             unit_price: int, room_id: int, state_id: int = 1) -> Item:
    """Добавить объект в коллекцию с новым ID."""
    new_id = max((item.id for item in data["items"]), default=0) + 1
    raw = {
        "id": new_id, "name": name.strip(), "category_id": category_id,
        "quantity": quantity, "unit_price": unit_price,
        "room_id": room_id, "state_id": state_id,
    }
    item = Item.from_dict(
        raw, data["categories"], data["conditions"], data["rooms"],
    )
    data["items"].append(item)
    return item


def change_state(data: dict, item_id: int, state_id: int) -> None:
    if type(state_id) is not int or state_id not in STATES:
        raise ValueError("Неизвестное состояние.")
    get_item(data, item_id).change_condition(data["conditions"][state_id])


def move_item(data: dict, item_id: int, room_id: int) -> None:
    """Связать объект перемещения с предметом и двумя помещениями."""
    item = get_item(data, item_id)
    if not can_move(item, room_id):
        raise ValueError("Нужны исправный предмет и другое помещение.")
    target = data["rooms"][room_id]
    move_id = max((move.id for move in data["moves"]), default=0) + 1
    move = Movement(
        move_id, item, item.room, target, datetime.now().isoformat(),
    )
    item.move_to(target)
    data["moves"].append(move)


def cancel_move(data: dict, move_id: int) -> None:
    move = next((m for m in data["moves"] if m.id == move_id), None)
    if move is None or move.cancelled:
        raise ValueError("Перемещение не найдено или уже отменено.")
    active = [m for m in data["moves"]
              if m.item is move.item and not m.cancelled]
    if active[-1] is not move:
        raise ValueError("Сначала отмените более позднее перемещение.")
    move.cancel()


def find_items(data: dict, query: str = "", category_id: int = 0,
               state_id: int = 0, room_id: int = 0) -> list[Item]:
    return [item for item in data["items"]
            if query.strip().casefold() in item.name.casefold()
            and (not category_id or item.category.id == category_id)
            and (not state_id or item.condition.id == state_id)
            and (not room_id or item.room.id == room_id)]


def sort_items(items: list[Item], by: str = "name") -> list[Item]:
    if by == "name":
        return sorted(items, key=lambda item: item.name.casefold())
    if by == "total":
        return sorted(items, key=lambda item: item.total)
    raise ValueError("Неизвестный способ сортировки.")


def statistics(data: dict) -> dict:
    items = data["items"]
    return {
        "batches": len(items),
        "units": sum(item.quantity for item in items),
        "total": sum(item.total for item in items),
        "usable": sum(i.quantity for i in items if i.condition.usable),
        "categories": len({item.category.id for item in items}),
    }


def format_item(item: Item) -> str:
    return str(item)
