"""Партия инвентаря объединяет данные и правила их изменения."""

from validation import check_item
from .references import Category, Condition, Room


class Item:
    """Одна партия одинаковых предметов в одном помещении."""

    def __init__(self, identifier: int, name: str, category: Category,
                 condition: Condition, room: Room, quantity: int,
                 unit_price: int) -> None:
        check_item({
            "id": identifier, "name": name, "category_id": category.id,
            "state_id": condition.id, "room_id": room.id,
            "quantity": quantity, "unit_price": unit_price,
        })
        self.id = identifier
        self.name = name.strip()
        self.category = category
        self._condition = condition
        self._room = room
        self._quantity = quantity
        self._unit_price = unit_price

    @property
    def condition(self) -> Condition:
        return self._condition

    @property
    def room(self) -> Room:
        return self._room

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def unit_price(self) -> int:
        return self._unit_price

    @property
    def total(self) -> int:
        return self.quantity * self.unit_price

    def usage_status(self) -> str:
        return self.condition.usage_status()

    def change_condition(self, condition: Condition) -> None:
        """Не допускать восстановления уже списанного инвентаря."""
        if self.condition.id == 3 and condition.id != 3:
            raise ValueError("Нельзя восстановить списанный предмет.")
        self._condition = condition

    def can_move(self, room: Room) -> bool:
        return self.condition.usable and self.room.id != room.id

    def move_to(self, room: Room) -> None:
        """Переместить исправную партию в другое помещение."""
        if not self.can_move(room):
            raise ValueError("Нужны исправный предмет и другое помещение.")
        self._room = room

    def restore_room(self, expected: Room, previous: Room) -> None:
        """Откат записи журнала, а не новое физическое перемещение."""
        if self.room.id != expected.id:
            raise ValueError("Текущее помещение не соответствует записи.")
        self._room = previous

    def handling_note(self) -> str:
        """Правило обращения; переопределяется для режущего инвентаря."""
        return "Соблюдайте обычные правила хранения."

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "category_id": self.category.id, "state_id": self.condition.id,
            "room_id": self.room.id, "quantity": self.quantity,
            "unit_price": self.unit_price,
        }

    @classmethod
    def from_dict(cls, raw: dict, categories: dict[int, Category],
                  conditions: dict[int, Condition],
                  rooms: dict[int, Room]) -> "Item":
        """Создать объект из JSON, восстановив ссылки на справочники."""
        check_item(raw)
        item_type = CuttingItem if raw["category_id"] == 2 else cls
        return item_type(
            raw["id"], raw["name"], categories[raw["category_id"]],
            conditions[raw["state_id"]], rooms[raw["room_id"]],
            raw["quantity"], raw["unit_price"],
        )

    def __str__(self) -> str:
        return (
            f"{self.id} — {self.name} | {self.category} | {self.condition}"
            f" | {self.room} | {self.quantity} шт."
            f" | {self.total // 100}.{self.total % 100:02d} руб."
        )


class CuttingItem(Item):
    """Режущий предмет является кухонным инвентарем."""

    def handling_note(self) -> str:
        return "Храните режущую кромку в защитном чехле."
