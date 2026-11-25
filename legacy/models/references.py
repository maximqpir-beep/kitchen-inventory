"""Объекты справочников предметной области."""


class Reference:
    """Именованная запись справочника с неизменяемым ID."""

    def __init__(self, identifier: int, name: str) -> None:
        if type(identifier) is not int or identifier <= 0 or not name.strip():
            raise ValueError("Неверная запись справочника.")
        self._id = identifier
        self._name = name.strip()

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self.name


class Category(Reference):
    """Категория, объединяющая сходные предметы."""


class Room(Reference):
    """Помещение, в котором находится партия."""


class Condition(Reference):
    """Состояние и связанное с ним разрешение использования."""

    @property
    def usable(self) -> bool:
        return self.id == 1

    def usage_status(self) -> str:
        if self.usable:
            return "Разрешен к использованию"
        return f"Использование запрещено: {self.name}"
