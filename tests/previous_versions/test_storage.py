"""Проверка сохранения, восстановления и защиты исходного файла."""

import json

import pytest

from catalog import demo_data
from inventory import export_data, import_data, move_item
from storage import load_data, save_data


def test_round_trip(tmp_path):
    path = tmp_path / "inventory.json"
    data = import_data(demo_data())
    move_item(data, 2, 3)
    save_data(data, path)
    assert export_data(load_data(path)) == export_data(data)


def test_first_start(tmp_path):
    path = tmp_path / "new" / "inventory.json"
    data = load_data(path)
    assert path.exists()
    assert len(export_data(data)["items"]) == 8


def test_corrupted_json_not_overwritten(tmp_path):
    path = tmp_path / "inventory.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError):
        load_data(path)
    assert path.read_text(encoding="utf-8") == "{broken"


@pytest.mark.parametrize("problem", ["duplicate", "missing", "reference",
                                     "quantity", "version"])
def test_invalid_schema(tmp_path, problem):
    raw = demo_data()
    if problem == "duplicate":
        raw["items"][1]["id"] = 1
    elif problem == "missing":
        del raw["items"][0]["name"]
    elif problem == "reference":
        raw["items"][0]["room_id"] = 999
    elif problem == "quantity":
        raw["items"][0]["quantity"] = True
    else:
        raw["version"] = 999
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError):
        load_data(path)


def test_failed_write_keeps_old_file(tmp_path, monkeypatch):
    path = tmp_path / "inventory.json"
    data = load_data(path)
    before = path.read_bytes()
    move_item(data, 1, 3)

    def deny_replace(*args):
        raise PermissionError("Нет доступа")

    monkeypatch.setattr("storage.os.replace", deny_replace)
    with pytest.raises(PermissionError):
        save_data(data, path)
    assert path.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


def test_invalid_history():
    raw = demo_data()
    raw["moves"] = [{
        "id": 1, "item_id": 999, "from_room": 1, "to_room": 3,
        "created_at": "2026-09-30T12:00:00", "cancelled": False,
    }]
    with pytest.raises(ValueError):
        import_data(raw)
