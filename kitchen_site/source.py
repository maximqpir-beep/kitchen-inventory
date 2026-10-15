"""Веб-слой читает объекты ПР3, не изменяя JSON при GET-запросах."""

from pathlib import Path

from django.conf import settings
from django.http import Http404

from inventory import find_items, get_item, sort_items
from storage import load_data


class DataUnavailable(Exception):
    """Хранилище отсутствует, повреждено или недоступно."""


def read_inventory() -> dict:
    path = Path(settings.INVENTORY_PATH)
    try:
        if not path.is_file():
            raise FileNotFoundError(path.name)
        return load_data(path)
    except (OSError, ValueError, UnicodeError) as error:
        raise DataUnavailable("Не удалось прочитать JSON.") from error


def find_item_or_404(data: dict, item_id: int):
    try:
        return get_item(data, item_id)
    except ValueError as error:
        raise Http404("Предмет не найден.") from error


def find_movement_or_404(data: dict, movement_id: int):
    for movement in data["moves"]:
        if movement.id == movement_id:
            return movement
    raise Http404("Перемещение не найдено.")


def select_items(data: dict, query: str) -> list:
    return sort_items(find_items(data, query), "name")
