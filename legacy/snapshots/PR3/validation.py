"""Проверка входных данных и формата JSON."""

from datetime import datetime

from catalog import CATEGORIES, ROOMS, STATES


def positive_int(value: int, label: str) -> None:
    """Отклонить нецелые, логические и неположительные значения."""
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label}: требуется положительное целое число.")


def check_item(item: dict) -> None:
    """Проверить одну партию, не изменяя ее."""
    if not isinstance(item, dict):
        raise ValueError("Предмет должен быть объектом JSON.")
    for field in ("id", "quantity", "unit_price"):
        positive_int(item.get(field), field)
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Название не должно быть пустым.")
    for field, options in (
        ("category_id", CATEGORIES), ("state_id", STATES),
        ("room_id", ROOMS),
    ):
        value = item.get(field)
        if type(value) is not int or value not in options:
            raise ValueError(f"Неизвестное значение {field}.")


def check_data(data: dict) -> None:
    """Проверить структуру, уникальность ID и цепочки перемещений."""
    if not isinstance(data, dict) or type(data.get("version")) is not int:
        raise ValueError("Неверный формат файла.")
    if data["version"] != 1:
        raise ValueError("Неподдерживаемая версия файла.")
    if not isinstance(data.get("items"), list):
        raise ValueError("items должен быть списком.")
    if not isinstance(data.get("moves"), list):
        raise ValueError("moves должен быть списком.")
    ids = set()
    for item in data["items"]:
        check_item(item)
        if item["id"] in ids:
            raise ValueError("Повторяющийся ID предмета.")
        ids.add(item["id"])
    move_ids = set()
    positions = {}
    for move in data["moves"]:
        if not isinstance(move, dict):
            raise ValueError("Перемещение должно быть объектом JSON.")
        positive_int(move.get("id"), "ID перемещения")
        positive_int(move.get("item_id"), "ID предмета")
        if move["id"] in move_ids or move["item_id"] not in ids:
            raise ValueError("Неверная ссылка или повтор ID перемещения.")
        move_ids.add(move["id"])
        for key in ("from_room", "to_room"):
            if type(move.get(key)) is not int or move[key] not in ROOMS:
                raise ValueError("Неизвестное помещение в истории.")
        if move["from_room"] == move["to_room"]:
            raise ValueError("Помещения перемещения совпадают.")
        if type(move.get("cancelled")) is not bool:
            raise ValueError("cancelled должен быть логическим значением.")
        if not isinstance(move.get("created_at"), str):
            raise ValueError("Отсутствует дата перемещения.")
        datetime.fromisoformat(move["created_at"])
        if not move["cancelled"]:
            old = positions.get(move["item_id"], move["from_room"])
            if old != move["from_room"]:
                raise ValueError("Нарушен порядок перемещений.")
            positions[move["item_id"]] = move["to_room"]
    for item in data["items"]:
        if positions.get(item["id"], item["room_id"]) != item["room_id"]:
            raise ValueError("Помещение предмета не соответствует истории.")
