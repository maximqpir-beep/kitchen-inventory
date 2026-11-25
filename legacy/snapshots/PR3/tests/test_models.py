"""Дополнительные проверки объектной модели ПР3."""

import pytest

from catalog import demo_data
from inventory import export_data, get_item, import_data, move_item
from models import CuttingItem, Item, Room


def test_classes_and_polymorphism():
    data = import_data(demo_data())
    pan = get_item(data, 1)
    knife = get_item(data, 2)
    assert isinstance(pan, Item)
    assert isinstance(knife, CuttingItem)
    assert isinstance(knife, Item)
    assert pan.handling_note() != knife.handling_note()
    assert "Нож" in str(knife)


def test_shared_object_references():
    data = import_data(demo_data())
    move_item(data, 1, 3)
    reloaded = import_data(export_data(data))
    item = get_item(reloaded, 1)
    move = reloaded["moves"][0]
    assert move.item is item
    assert move.target is item.room
    assert item.room is reloaded["rooms"][3]
    assert isinstance(item.room, Room)


def test_properties_protect_direct_assignment():
    item = get_item(import_data(demo_data()), 1)
    with pytest.raises(AttributeError):
        item.quantity = -1
    with pytest.raises(AttributeError):
        item.room = Room(3, "Склад")


def test_old_pr2_json_is_compatible():
    raw = demo_data()
    assert export_data(import_data(raw)) == raw
