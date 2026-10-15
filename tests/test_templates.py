"""Проверка требований к шаблонам ПР6."""

import ast
from pathlib import Path

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
import pytest

from catalog import demo_data
from homepage.templatetags.inventory_tags import money
from inventory import import_data, move_item
from storage import save_data


@pytest.fixture
def page_data(tmp_path, settings):
    settings.INVENTORY_PATH = tmp_path / "inventory.json"
    data = import_data(demo_data())
    move_item(data, 1, 3)
    save_data(data, settings.INVENTORY_PATH)
    return data


@pytest.mark.parametrize("url,template", [
    ("/", "homepage/index.html"),
    ("/items/", "items/item_list.html"),
    ("/items/1/", "items/item_detail.html"),
    ("/movements/", "movements/movement_list.html"),
    ("/movements/1/", "movements/movement_detail.html"),
])
def test_template_and_base_used(client, page_data, url, template):
    response = client.get(url)
    names = {t.name for t in response.templates}
    assert template in names
    assert "base.html" in names
    assert "includes/navigation.html" in names


def test_objects_in_context(client, page_data):
    response = client.get("/items/1/")
    assert response.context["item"].name == "Кастрюля 5 л"
    assert response.context["item"].room.name == "Склад"


def test_filters_and_default():
    assert money(125050) == "1 250.50"
    html = render_to_string("items/includes/item_card.html", {
        "item": {"id": 1, "name": "Очень длинное название " * 5,
                 "total": 125050},
    })
    assert "Без категории" in html
    assert "1 250.50" in html
    assert "…" in html


def test_own_assets():
    for asset in ("homepage/js/catalog.js", "homepage/img/logo.svg",
                  "homepage/img/kitchen.svg"):
        assert finders.find(asset)


def test_views_no_html_builder():
    root = Path(__file__).resolve().parents[1]
    assert not (root / "homepage/html.py").exists()
    for app in ("homepage", "items", "movements"):
        tree = ast.parse((root / app / "views.py").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                assert "<html" not in node.value
                assert "<div" not in node.value
                assert "<h1" not in node.value
