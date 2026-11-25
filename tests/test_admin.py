from datetime import timedelta

from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
import pytest

from items.models import Item, Room
from movements.models import Movement
from movements.services import cancel_movement, complete_movement, save_plan

pytestmark = pytest.mark.django_db


def test_generated_cost_and_slug(client, inventory_db):
    item = Item.objects.get(pk=1)
    item.quantity = 3
    item.save(update_fields=["quantity"])
    item.refresh_from_db()
    assert item.total == 3 * item.unit_price
    room = Room.objects.get(pk=1)
    assert room.slug.isascii()
    assert client.get(room.get_absolute_url()).status_code == 200
    assert client.get("/rooms/does-not-exist/").status_code == 404
    assert client.get("/rooms/").status_code == 200


def test_status_queries_and_plan_conflict(inventory_db):
    assert Movement.objects.completed().count() == 2
    assert Movement.objects.cancelled().count() == 1
    assert not Movement.objects.active().exists()
    item = Item.objects.get(pk=3)
    plan = save_plan(
        Movement(item=item, target_id=4, scheduled_for=timezone.localdate())
    )
    assert plan.pk in Movement.objects.active().values_list("pk", flat=True)
    assert Movement.objects.for_date(timezone.localdate()).count() == 1
    duplicate = Movement(
        item=item, target_id=2, scheduled_for=timezone.localdate()
    )
    with pytest.raises(ValidationError):
        save_plan(duplicate)
    complete_movement(plan.pk)
    item.refresh_from_db()
    assert item.room_id == 4
    cancel_movement(plan.pk)
    item.refresh_from_db()
    assert item.room_id == 1
    assert Movement.objects.get(pk=plan.pk).status == "CANCELLED"


def test_failed_transitions_preserve_data(inventory_db):
    item = Item.objects.get(pk=3)
    plan = save_plan(
        Movement(
            item=item,
            target_id=4,
            scheduled_for=timezone.localdate() + timedelta(days=1),
        )
    )
    with pytest.raises(ValidationError, match="не наступила"):
        complete_movement(plan.pk)
    cancel_movement(plan.pk)
    with pytest.raises(ValidationError, match="уже отменена"):
        cancel_movement(plan.pk)
    item.refresh_from_db()
    assert item.room_id == 1


def test_admin_requires_permissions(client, inventory_db):
    assert client.get("/admin/").status_code == 302
    user = User.objects.create_user(
        "viewer", password="test-only", is_staff=True
    )
    user.user_permissions.add(Permission.objects.get(codename="view_item"))
    client.force_login(user)
    assert client.get("/admin/items/item/").status_code == 200
    assert client.get("/admin/items/item/add/").status_code == 403
    assert client.post("/admin/items/item/1/delete/").status_code == 403


def test_admin_lists_search_and_inlines(admin_client, inventory_db):
    for url in (
        "/admin/",
        "/admin/items/item/",
        "/admin/items/room/",
        "/admin/movements/movement/",
        "/admin/items/item/2/change/",
        "/admin/items/room/1/change/",
    ):
        assert admin_client.get(url).status_code == 200
    response = admin_client.get("/admin/items/item/", {"q": "Нож"})
    assert response.context["cl"].result_count == 1
    response = admin_client.get(
        "/admin/movements/movement/", {"status__exact": "CANCELLED"}
    )
    assert response.context["cl"].result_count == 1
    response = admin_client.get("/admin/items/item/2/change/")
    assert len(response.context["inline_admin_formsets"]) == 1


def test_admin_action_uses_business_logic(inventory_db):
    from django.contrib.auth.models import AnonymousUser

    request = RequestFactory().post("/admin/movements/movement/")
    request.user = AnonymousUser()
    request.session = {}
    request._messages = FallbackStorage(request)
    model_admin = admin.site._registry[Movement]
    model_admin.cancel_selected(request, Movement.objects.filter(pk=1))
    assert Movement.objects.get(pk=1).status == "CANCELLED"
    assert Item.objects.get(pk=2).room_id == 1


@pytest.mark.django_db(transaction=True)
def test_migration_preserves_cancelled_and_completed():
    from django.db.migrations.executor import MigrationExecutor

    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes()
    old = [("items", "0001_initial"), ("movements", "0001_initial")]
    executor.migrate(old)
    try:
        apps = executor.loader.project_state(old).apps
        cat = apps.get_model("items", "Category").objects.create(
            name="Посуда", name_search="посуда"
        )
        state = apps.get_model("items", "Condition").objects.create(
            name="Исправен", name_search="исправен", usable=True
        )
        room = apps.get_model("items", "Room").objects.create(
            name="Цех", name_search="цех"
        )
        target = apps.get_model("items", "Room").objects.create(
            name="Склад", name_search="склад"
        )
        item = apps.get_model("items", "Item").objects.create(
            name="Нож",
            name_search="нож",
            category=cat,
            condition=state,
            room=target,
            quantity=1,
            unit_price=100,
        )
        model = apps.get_model("movements", "Movement")
        model.objects.create(
            item=item, source=room, target=target, cancelled=False
        )
        model.objects.create(
            item=item, source=target, target=room, cancelled=True
        )
        executor = MigrationExecutor(connection)
        executor.migrate(latest)
        assert list(
            Movement.objects.order_by("pk").values_list("status", flat=True)
        ) == ["COMPLETED", "CANCELLED"]
        assert Room.objects.exclude(slug="").count() == 2
        assert Item.objects.get(pk=item.pk).room_id == target.pk
    finally:
        MigrationExecutor(connection).migrate(latest)
