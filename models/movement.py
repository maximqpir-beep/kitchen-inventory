"""Запись связывает предмет с исходным и целевым помещением."""

from .item import Item
from .references import Room


class Movement:
    """Перемещение партии с возможностью отмены."""

    def __init__(self, identifier: int, item: Item, source: Room,
                 target: Room, created_at: str,
                 cancelled: bool = False) -> None:
        self.id = identifier
        self.item = item
        self.source = source
        self.target = target
        self.created_at = created_at
        self._cancelled = cancelled

    @property
    def cancelled(self) -> bool:
        return self._cancelled

    def cancel(self) -> None:
        """Отменить запись; очередность проверяет функция коллекции."""
        if self.cancelled:
            raise ValueError("Перемещение уже отменено.")
        self.item.restore_room(self.target, self.source)
        self._cancelled = True

    def to_dict(self) -> dict:
        return {
            "id": self.id, "item_id": self.item.id,
            "from_room": self.source.id, "to_room": self.target.id,
            "created_at": self.created_at, "cancelled": self.cancelled,
        }

    def __str__(self) -> str:
        status = "отменено" if self.cancelled else "выполнено"
        return (
            f"{self.id}: {self.item.name}, {self.source} -> "
            f"{self.target}, {status}"
        )
