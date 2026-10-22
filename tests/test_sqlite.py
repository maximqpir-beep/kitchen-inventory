"""Миграция, ограничения, SQL и работа сайта с независимой базой."""

from contextlib import closing
import json
import sqlite3

import pytest

from catalog import demo_data
from db.database import QUERIES, fetch_all, fetch_one, get_connection
from db.import_json import import_json
from db.verify_queries import EXAMPLES
from inventory import cancel_move, change_state, import_data, move_item
from storage import save_data


@pytest.fixture
def sql_data(tmp_path, settings):
    source = tmp_path / "inventory.json"
    target = tmp_path / "inventory.sqlite"
    settings.INVENTORY_PATH = source
    settings.DATABASE_PATH = target
    settings.DEBUG = False
    data = import_data(demo_data())
    move_item(data, 2, 3)
    move_item(data, 1, 2)
    cancel_move(data, 2)
    change_state(data, 4, 2)
    change_state(data, 5, 3)
    save_data(data, source)
    import_json(source, target)
    return source, target


def test_import_preserves_every_record_and_foreign_keys(sql_data):
    source, target = sql_data
    raw = json.loads(source.read_text())
    with closing(get_connection(target)) as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        items = [dict(row) for row in conn.execute(
            "SELECT id, name, category_id, state_id, room_id, quantity, "
            "unit_price FROM items ORDER BY id")]
        assert items == raw["items"]
        moves = [dict(row) for row in conn.execute(
            "SELECT * FROM movements ORDER BY id")]
        assert moves == raw["moves"]
        assert conn.execute(
            "SELECT COUNT(*) FROM rooms WHERE description IS NULL"
        ).fetchone()[0] == 4


@pytest.mark.parametrize("statement", [
    "UPDATE items SET room_id=999 WHERE id=1",
    "UPDATE items SET quantity=0 WHERE id=1",
    "UPDATE items SET unit_price=-1 WHERE id=1",
    "UPDATE movements SET cancelled=2 WHERE id=1",
    "UPDATE movements SET to_room=from_room WHERE id=1",
    "DELETE FROM rooms WHERE id=1",
])
def test_constraints_reject_invalid_data(sql_data, statement):
    _, target = sql_data
    with closing(get_connection(target)) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(statement)


def test_reimport_requires_explicit_replace(sql_data):
    source, target = sql_data
    before = target.read_bytes()
    with pytest.raises(ValueError, match="--replace"):
        import_json(source, target)
    assert target.read_bytes() == before
    import_json(source, target, replace=True)
    assert fetch_one("inventory_totals", path=target)["batches"] == 8


def test_bad_json_and_failed_insert_preserve_database(sql_data):
    source, target = sql_data
    before = fetch_all("items", ("%", 0, 0, 0, 0, 0, 0), path=target)
    source.write_text('{"version": 1, "items": [], "moves": [{}]}')
    with pytest.raises(ValueError):
        import_json(source, target, replace=True)
    raw = demo_data()
    raw["items"][0]["quantity"] = 2 ** 80
    source.write_text(json.dumps(raw))
    with pytest.raises(OverflowError):
        import_json(source, target, replace=True)
    assert fetch_all("items", ("%", 0, 0, 0, 0, 0, 0), path=target) == before


def test_sql_aggregates_and_zero_groups(sql_data):
    _, target = sql_data
    totals = fetch_one("inventory_totals", path=target)
    assert dict(totals) == {"batches": 8, "units": 8, "total": 655050,
                            "usable": 6}
    assert dict(fetch_one("movement_totals", path=target)) == {
        "total": 2, "done": 1, "cancelled": 1,
    }
    grouped = fetch_all("room_statistics", path=target)
    assert len(grouped) == 4
    assert grouped[3]["units"] == 0  # LEFT JOIN сохраняет пустую Моечную.
    assert fetch_all("heavy_rooms", (999,), path=target) == []
    heavy = fetch_all("heavy_rooms", (6,), path=target)
    assert heavy[0]["name"] == "Горячий цех"


def test_every_sql_query_is_executable(sql_data):
    _, target = sql_data
    assert len(QUERIES) >= 10
    with closing(get_connection(target, readonly=True)) as conn:
        for name, query in QUERIES.items():
            conn.execute(query, EXAMPLES[name]).fetchall()


@pytest.mark.parametrize("url", [
    "/rooms/", "/statistics/", "/items/available/",
])
def test_new_pages_and_navigation(client, sql_data, url):
    response = client.get(url)
    assert response.status_code == 200
    assert 'href="/statistics/"' in response.content.decode()
    assert 'href="/rooms/"' in response.content.decode()
    assert client.post(url).status_code == 405


def test_every_query_reaches_a_web_page(client, sql_data, monkeypatch):
    import kitchen_site.source as source
    called = set()
    original = source.fetch_all

    def track(name, parameters=(), **kwargs):
        called.add(name)
        return original(name, parameters, **kwargs)

    monkeypatch.setattr(source, "fetch_all", track)
    # fetch_one использует собственный модуль; отслеживаем и его вызовы.
    original_one = source.fetch_one

    def track_one(name, parameters=(), **kwargs):
        called.add(name)
        return original_one(name, parameters, **kwargs)

    monkeypatch.setattr(source, "fetch_one", track_one)
    for url in ("/", "/rooms/", "/items/", "/items/1/",
                "/items/available/", "/movements/", "/movements/1/",
                "/statistics/"):
        assert client.get(url).status_code == 200
    assert called == set(QUERIES)


def test_combined_search_and_usable_filter(client, sql_data):
    response = client.get("/items/", {"q": "НОЖ", "room": 3, "state": 1,
                                      "category": 2})
    assert [r["id"] for r in response.context["items"]] == [2]
    response = client.get("/items/available/", {"room": 1})
    assert len(response.context["items"]) == 5
    assert all(r["usable"] for r in response.context["items"])
    assert "Доска разделочная" not in response.content.decode()


@pytest.mark.parametrize("query", ["' OR 1=1 --", "%", "_", "\\"])
def test_user_search_is_literal_and_parameterized(client, sql_data, query):
    response = client.get("/items/", {"q": query})
    assert response.status_code == 200
    assert list(response.context["items"]) == []


def test_movement_date_status_and_pagination(client, sql_data):
    source, _ = sql_data
    date = json.loads(source.read_text())["moves"][0]["created_at"][:10]
    response = client.get("/movements/", {"date": date, "status": 0})
    assert len(response.context["entries"]) == 1
    assert not response.context["entries"][0]["movement"]["cancelled"]
    response = client.get("/movements/", {"date": "2000-01-01"})
    assert not response.context["entries"]
    assert client.get("/movements/", {"page": 2}).status_code == 200


@pytest.mark.parametrize("url,parameters", [
    ("/items/", {"room": "x"}), ("/items/", {"state": -1}),
    ("/items/available/", {"room": "' OR 1=1"}),
    ("/movements/", {"date": "2026-02-30"}),
    ("/movements/", {"date": "20261015"}),
    ("/movements/", {"status": 2}), ("/movements/", {"page": 0}),
    ("/statistics/", {"min_units": -2}),
])
def test_bad_parameters_return_400(client, sql_data, url, parameters):
    assert client.get(url, parameters).status_code == 400


def test_sqlite_is_source_of_truth_and_json_is_retained(client, sql_data):
    source, target = sql_data
    before = source.read_bytes()
    with closing(get_connection(target)) as conn:
        conn.execute("UPDATE items SET name=? WHERE id=1", ("Из SQLite",))
        conn.commit()
    assert "Из SQLite" in client.get("/items/1/").content.decode()
    source.unlink()
    assert client.get("/").status_code == 200
    source.write_bytes(before)


def test_empty_database_statistics_and_search(client, sql_data):
    source, target = sql_data
    source.write_text(json.dumps({"version": 1, "items": [], "moves": []}))
    import_json(source, target, replace=True)
    assert fetch_one("inventory_totals", path=target)["total"] == 0
    assert fetch_one("price_bounds", path=target)["minimum"] is None
    html = client.get("/statistics/").content.decode()
    assert "нет данных" in html
    assert "None" not in html
    assert client.get("/items/available/").status_code == 200
