from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test.utils import CaptureQueriesContext
from django.db import connection
import pytest

from apps.items.models import Category, Condition, Item, Room
from config import orm
from apps.movements.models import Movement


@pytest.mark.django_db
def test_import_and_links(inventory_db):
    assert Item.objects.count() == 8
    assert Movement.objects.count() == 3
    assert Room.objects.count() == 4
    knife = Item.objects.get(pk=2)
    assert knife.room.name == "Склад"
    assert knife.category.name == "Режущий инвентарь"
    assert knife.movements.get().source.name == "Горячий цех"
    with pytest.raises(CommandError, match="не пуста"):
        call_command("import_legacy")
    assert Item.objects.count() == 8


@pytest.mark.django_db
def test_totals_groups(inventory_db):
    assert orm.totals() == dict(batches=8, units=8, usable=6, total=655050)
    groups = list(orm.grouped(Room))
    assert groups[-1]["units"] == 0
    assert sum(x["units"] for x in groups) == 8
    assert orm.item_list().exclude(condition__usable=False).count() == 6


@pytest.mark.django_db
def test_crud_and_protect(inventory_db):
    room = Room.objects.create(name="Проверка")
    room.description = "Новое описание"
    room.save()
    assert Room.objects.get(pk=room.pk).description == "Новое описание"
    room.delete()
    assert not Room.objects.filter(name="Проверка").exists()
    from django.db.models import ProtectedError

    with pytest.raises(ProtectedError):
        Room.objects.get(pk=1).delete()
    with pytest.raises(IntegrityError), transaction.atomic():
        Item.objects.filter(pk=1).update(quantity=0)


@pytest.mark.django_db
def test_no_n_plus_one(inventory_db):
    with CaptureQueriesContext(connection) as queries:
        rows = list(orm.item_list())
        names = [
            (x.category.name, x.condition.name, x.room.name) for x in rows
        ]
    assert len(names) == 8
    assert len(queries) == 1
    with CaptureQueriesContext(connection) as queries:
        for move in orm.movement_list():
            str(move.item), str(move.source), str(move.target)
    assert len(queries) == 1


@pytest.mark.django_db
def test_demo_rolls_back(inventory_db):
    before = Room.objects.count()
    call_command("orm_demo", stdout=StringIO())
    assert Room.objects.count() == before


@pytest.mark.django_db
def test_empty_statistics():
    assert orm.totals()["batches"] == 0
    assert orm.totals()["total"] == 0
    assert list(orm.grouped(Category)) == []
    assert Condition.objects.count() == 0
