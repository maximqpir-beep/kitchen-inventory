import pytest

from items.models import Item

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "url,text",
    [
        ("/", "Все на своем месте"),
        ("/items/", "Кастрюля 5 л"),
        ("/items/2/", "Нож поварской"),
        ("/movements/", "Отменено"),
        ("/movements/1/", "Перемещение выполнено"),
        ("/rooms/", "Горячий цех"),
        ("/statistics/", "Статистика"),
        ("/items/available/", "Пригодный"),
    ],
)
def test_pages(client, inventory_db, url, text):
    result = client.get(url)
    assert result.status_code == 200
    assert text in result.content.decode()
    assert "base.html" in {t.name for t in result.templates}


@pytest.mark.parametrize(
    "url", ["/unknown/", "/items/999/", "/movements/999/"]
)
def test_404(client, inventory_db, url):
    assert client.get(url).status_code == 404


def test_filters_and_empty(client, inventory_db):
    response = client.get("/items/", {"q": "НОЖ", "room": 3, "state": 1})
    assert [x.pk for x in response.context["items"]] == [2]
    assert not client.get("/items/", {"q": "' OR 1=1 --"}).context["items"]
    assert len(client.get("/items/available/").context["items"]) == 6
    assert not client.get("/movements/", {"date": "2000-01-01"}).context[
        "entries"
    ]


@pytest.mark.parametrize(
    "url,params",
    [
        ("/items/", {"room": "bad"}),
        ("/items/", {"sort": "drop table"}),
        ("/movements/", {"date": "2026-02-30"}),
        ("/movements/", {"page": 0}),
        ("/statistics/", {"min_units": -1}),
    ],
)
def test_bad_parameters(client, inventory_db, url, params):
    assert client.get(url, params).status_code == 400


def test_sqlite_updates_visible(client, inventory_db):
    item = Item.objects.get(pk=1)
    item.name = "<script>x</script>"
    item.save()
    html = client.get(item.get_absolute_url()).content.decode()
    assert "<script>x</script>" not in html
    assert "&lt;script&gt;" in html


def test_pagination_keeps_filters(client, inventory_db):
    original = Item.objects.first()
    for n in range(25):
        Item.objects.create(
            name=f"Нож {n}",
            category=original.category,
            condition=original.condition,
            room=original.room,
            quantity=1,
            unit_price=100,
        )
    response = client.get("/items/", {"q": "нож", "sort": "price", "page": 1})
    assert "q=%D0%BD%D0%BE%D0%B6" in response.context["following"]
    assert "sort=price" in response.context["following"]
    assert len(response.context["items"]) == 20


def test_readonly(client, inventory_db):
    for url in ("/", "/items/", "/movements/", "/statistics/"):
        assert client.post(url).status_code == 405
