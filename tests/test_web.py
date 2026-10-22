"""Веб-регрессии: страницы, связи, ошибки и отсутствие записи при GET."""

from pathlib import Path

from django.contrib.staticfiles import finders
from django.urls import resolve, reverse
import pytest

from catalog import demo_data
from inventory import (
    cancel_move, change_state, import_data, move_item,
)
from storage import save_data
from db.import_json import import_json


def save_web_data(data, settings):
    save_data(data, settings.INVENTORY_PATH)
    import_json(settings.INVENTORY_PATH, settings.DATABASE_PATH, replace=True)


@pytest.fixture
def web_data(tmp_path, settings):
    path = tmp_path / "inventory.json"
    settings.INVENTORY_PATH = path
    settings.DATABASE_PATH = tmp_path / "inventory.sqlite"
    settings.DEBUG = False
    data = import_data(demo_data())
    move_item(data, 2, 3)
    move_item(data, 1, 2)
    cancel_move(data, 2)
    change_state(data, 4, 2)
    change_state(data, 5, 3)
    save_web_data(data, settings)
    return data


@pytest.mark.parametrize("url,text", [
    ("/", "Все на своем месте"),
    ("/items/", "Кастрюля 5 л"),
    ("/items/2/", "Нож поварской"),
    ("/movements/", "Отменено"),
    ("/movements/1/", "Перемещение выполнено"),
])
def test_five_pages(client, web_data, url, text):
    response = client.get(url)
    assert response.status_code == 200
    assert text in response.content.decode()
    assert response["Content-Type"].startswith("text/html")


@pytest.mark.parametrize("url", [
    "/unknown/", "/items/999/", "/movements/999/", "/items/abc/",
])
def test_custom_404(client, web_data, url):
    response = client.get(url)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()
    assert "Кухонный учет" in response.content.decode()


def test_namespaces():
    assert reverse("items:detail", args=[2]) == "/items/2/"
    assert reverse("movements:detail", args=[1]) == "/movements/1/"
    assert resolve("/items/2/").kwargs == {"item_id": 2}


def test_search_and_no_results(client, web_data):
    response = client.get("/items/", {"q": "НОЖ"})
    content = response.content.decode()
    assert "Нож поварской" in content
    assert "Кастрюля 5 л" not in content
    response = client.get("/items/", {"q": "несуществующий предмет"})
    assert "Предметы не найдены" in response.content.decode()


def test_statuses_and_related_objects(client, web_data):
    content = client.get("/items/").content.decode()
    assert "требует ремонта" in content and "списан" in content
    content = client.get("/items/2/").content.decode()
    assert "Склад" in content and "защитном чехле" in content
    content = client.get("/movements/1/").content.decode()
    assert 'href="/items/2/"' in content
    assert "Горячий цех" in content and "Склад" in content
    content = client.get("/movements/2/").content.decode()
    assert "Запись отменена" in content


def test_empty_collections(client, settings, web_data):
    data = import_data({"version": 1, "items": [], "moves": []})
    save_web_data(data, settings)
    assert client.get("/").status_code == 200
    assert "Предметы не найдены" in client.get("/items/").content.decode()
    assert "Перемещений пока нет" in client.get("/movements/").content.decode()


def test_escape_names_and_query(client, settings, web_data):
    web_data["items"][0].name = '<script>alert("x")</script>'
    save_web_data(web_data, settings)
    for url in ("/items/", "/items/1/"):
        content = client.get(url).content.decode()
        assert '<script>alert("x")</script>' not in content
        assert "&lt;script&gt;" in content
    content = client.get("/items/", {"q": '"><script>x</script>'}).content
    assert b'<script>x</script>' not in content


@pytest.mark.parametrize("url", ["/", "/items/", "/movements/"])
def test_read_only_and_head(client, settings, web_data, url):
    before = settings.INVENTORY_PATH.read_bytes()
    database_before = settings.DATABASE_PATH.read_bytes()
    assert client.get(url).status_code == 200
    assert client.head(url).status_code == 200
    assert client.post(url, {"name": "changed"}).status_code == 405
    assert settings.INVENTORY_PATH.read_bytes() == before
    assert settings.DATABASE_PATH.read_bytes() == database_before


def test_reimport_updates_visible_without_restart(client, settings, web_data):
    web_data["items"][0].name = "Обновленная кастрюля"
    save_web_data(web_data, settings)
    assert "Обновленная кастрюля" in client.get("/items/1/").content.decode()


@pytest.mark.parametrize("problem", ["missing", "broken", "wrong_schema"])
def test_storage_errors_do_not_overwrite(client, settings, web_data, problem):
    path = settings.DATABASE_PATH
    if problem == "missing":
        path.unlink()
    else:
        path.write_text("{broken" if problem == "broken" else "{}")
    before = path.read_bytes() if path.exists() else None
    response = client.get("/items/")
    assert response.status_code == 503
    assert "Данные временно недоступны" in response.content.decode()
    after = path.read_bytes() if path.exists() else None
    assert after == before


def test_static_assets_exist():
    for asset in ("homepage/css/style.css",
                  "homepage/vendor/bootstrap.min.css"):
        result = finders.find(asset)
        assert result and Path(result).stat().st_size > 0
