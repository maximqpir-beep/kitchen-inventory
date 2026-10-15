"""Проверки правил предметной области, общие для ПР2 и ПР3."""

import pytest

from catalog import demo_data
from inventory import (
    add_item, calculate_total, cancel_move, change_state, export_data,
    find_items, get_item, get_usage_status, import_data, move_item,
    sort_items, statistics,
)


@pytest.fixture
def data():
    return import_data(demo_data())


def test_initial_total(data):
    assert calculate_total(get_item(data, 1)) == 125050


def test_add_batch(data):
    add_item(data, "Ложка", 4, 3, 12550, 3)
    item = export_data(data)["items"][-1]
    assert item["id"] == 9
    assert item["name"] == "Ложка"
    assert calculate_total(get_item(data, 9)) == 37650


@pytest.mark.parametrize("quantity", [0, -1, True, 1.5])
def test_invalid_quantity_does_not_add(data, quantity):
    before = export_data(data)
    with pytest.raises(ValueError):
        add_item(data, "Ложка", 4, quantity, 100, 1)
    assert export_data(data) == before


def test_empty_name(data):
    with pytest.raises(ValueError):
        add_item(data, "  ", 4, 1, 100, 1)


@pytest.mark.parametrize(
    "category,price,room", [(99, 100, 1), (1, 0, 1), (1, 100, 99)],
)
def test_bad_fields(data, category, price, room):
    with pytest.raises(ValueError):
        add_item(data, "Предмет", category, 1, price, room)


def test_search_case_and_filters(data):
    found = find_items(data, " НОЖ ", category_id=2, room_id=1)
    assert len(found) == 1
    assert not find_items(data, "нож", category_id=1)
    assert not find_items(data, state_id=2)


def test_sort_and_statistics(data):
    original = export_data(data)
    ordered = sort_items(find_items(data), "total")
    assert calculate_total(ordered[0]) == 28000
    assert calculate_total(ordered[-1]) == 180000
    result = statistics(data)
    assert result == {"batches": 8, "units": 8, "total": 655050,
                      "usable": 8, "categories": 5}
    assert export_data(data) == original


def test_move_and_cancel(data):
    move_item(data, 1, 3)
    assert export_data(data)["items"][0]["room_id"] == 3
    cancel_move(data, 1)
    raw = export_data(data)
    assert raw["items"][0]["room_id"] == 1
    assert raw["moves"][0]["cancelled"] is True


@pytest.mark.parametrize("state", [2, 3])
def test_unusable_cannot_move(data, state):
    change_state(data, 1, state)
    assert "запрещено" in get_usage_status(get_item(data, 1))
    with pytest.raises(ValueError):
        move_item(data, 1, 3)
    assert not export_data(data)["moves"]


@pytest.mark.parametrize("room", [1, 99, True])
def test_invalid_destination(data, room):
    with pytest.raises(ValueError):
        move_item(data, 1, room)


def test_cancel_order(data):
    move_item(data, 1, 3)
    move_item(data, 1, 4)
    with pytest.raises(ValueError):
        cancel_move(data, 1)
    cancel_move(data, 2)
    cancel_move(data, 1)
    assert export_data(data)["items"][0]["room_id"] == 1
    with pytest.raises(ValueError):
        cancel_move(data, 1)


def test_cancel_other_item_independent(data):
    move_item(data, 1, 3)
    move_item(data, 2, 4)
    cancel_move(data, 1)
    assert export_data(data)["items"][1]["room_id"] == 4


def test_written_off_is_final(data):
    change_state(data, 1, 3)
    with pytest.raises(ValueError):
        change_state(data, 1, 1)


def test_missing_item(data):
    with pytest.raises(ValueError):
        get_item(data, 999)


def test_empty_inventory():
    empty = import_data({"version": 1, "items": [], "moves": []})
    assert statistics(empty)["total"] == 0
    assert find_items(empty) == []
    add_item(empty, "Ложка", 4, 1, 100, 1)
    assert export_data(empty)["items"][0]["id"] == 1
