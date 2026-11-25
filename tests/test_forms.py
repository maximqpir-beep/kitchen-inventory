from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.utils import timezone
from PIL import Image
import pytest

from items.models import Item
from movements.models import Movement
from movements.services import save_plan

pytestmark = pytest.mark.django_db


@pytest.fixture
def plan_data():
    return {
        "item": 3,
        "target": 4,
        "scheduled_for": timezone.localdate().isoformat(),
        "note": "Проверка формы",
    }


def test_create_redirect_and_hidden_fields_ignored(
    admin_client, inventory_db, plan_data
):
    before = Movement.objects.count()
    response = admin_client.post(
        "/movements/create/",
        {
            **plan_data,
            "status": "COMPLETED",
            "source": 3,
        },
    )
    assert response.status_code == 302
    move = Movement.objects.latest("pk")
    assert Movement.objects.count() == before + 1
    assert move.status == "PLANNED"
    assert move.source_id == 1
    assert Item.objects.get(pk=3).room_id == 1
    assert response.url == move.get_absolute_url()
    # Обновление GET после PRG не создает повторную запись.
    admin_client.get(response.url)
    assert Movement.objects.count() == before + 1


@pytest.mark.parametrize(
    "changes,field",
    [
        ({"scheduled_for": "2000-01-01"}, "scheduled_for"),
        ({"scheduled_for": "2026-02-30"}, "scheduled_for"),
        ({"target": 1}, "target"),
        ({"item": 4}, "item"),
        ({"item": 9999}, "item"),
        ({"target": ""}, "target"),
    ],
)
def test_invalid_form_does_not_save(
    admin_client, inventory_db, plan_data, changes, field
):
    before = Movement.objects.count()
    response = admin_client.post(
        "/movements/create/", {**plan_data, **changes}
    )
    assert response.status_code == 200
    assert field in response.context["form"].errors
    assert Movement.objects.count() == before
    assert b"csrfmiddlewaretoken" in response.content


def test_conflict_edit_and_cancel_releases_slot(
    admin_client, inventory_db, plan_data
):
    admin_client.post("/movements/create/", plan_data)
    move = Movement.objects.latest("pk")
    response = admin_client.post(
        "/movements/create/", {**plan_data, "target": 2}
    )
    assert response.status_code == 200
    assert "item" in response.context["form"].errors
    response = admin_client.post(
        f"/movements/{move.pk}/edit/", {**plan_data, "target": 2}
    )
    assert response.status_code == 302
    move.refresh_from_db()
    assert move.target_id == 2
    assert Movement.objects.active().count() == 1
    assert admin_client.get(f"/movements/{move.pk}/cancel/").status_code == 405
    assert (
        admin_client.post(f"/movements/{move.pk}/cancel/").status_code == 302
    )
    move.refresh_from_db()
    assert move.status == "CANCELLED"
    assert (
        admin_client.post("/movements/create/", plan_data).status_code == 302
    )
    assert Movement.objects.active().count() == 1


def test_completion_then_cancellation_changes_room(
    admin_client, inventory_db, plan_data
):
    admin_client.post("/movements/create/", plan_data)
    move = Movement.objects.latest("pk")
    assert (
        admin_client.get(f"/movements/{move.pk}/complete/").status_code == 405
    )
    admin_client.post(f"/movements/{move.pk}/complete/")
    move.refresh_from_db()
    assert move.status == "COMPLETED"
    assert Item.objects.get(pk=3).room_id == 4
    assert admin_client.get(f"/movements/{move.pk}/edit/").status_code == 400
    admin_client.post(f"/movements/{move.pk}/cancel/")
    assert Item.objects.get(pk=3).room_id == 1


def test_stale_plan_rejected_and_history_order_preserved(
    admin_client, inventory_db, plan_data
):
    first = save_plan(
        Movement(item_id=3, target_id=4, scheduled_for=timezone.localdate())
    )
    admin_client.post(f"/movements/{first.pk}/complete/")
    second = save_plan(
        Movement(item_id=3, target_id=2, scheduled_for=timezone.localdate())
    )
    admin_client.post(f"/movements/{second.pk}/complete/")
    response = admin_client.post(f"/movements/{first.pk}/cancel/", follow=True)
    assert "более позднее" in response.content.decode()
    assert Item.objects.get(pk=3).room_id == 2
    admin_client.post(f"/movements/{second.pk}/cancel/")
    admin_client.post(f"/movements/{first.pk}/cancel/")
    assert Item.objects.get(pk=3).room_id == 1


def test_future_execution_and_repaired_item_rejected(
    admin_client, inventory_db, plan_data
):
    future = timezone.localdate() + timedelta(days=1)
    admin_client.post(
        "/movements/create/",
        {**plan_data, "scheduled_for": future.isoformat()},
    )
    move = Movement.objects.latest("pk")
    response = admin_client.post(
        f"/movements/{move.pk}/complete/", follow=True
    )
    assert "не наступила" in response.content.decode()
    move.scheduled_for = timezone.localdate()
    move.save()
    Item.objects.filter(pk=3).update(condition_id=2)
    response = admin_client.post(
        f"/movements/{move.pk}/complete/", follow=True
    )
    assert "неисправен" in response.content.decode()
    assert Item.objects.get(pk=3).room_id == 1


def test_auth_and_permissions(client, inventory_db, plan_data):
    assert client.get("/movements/create/").status_code == 302
    assert client.post("/movements/create/", plan_data).status_code == 302
    user = User.objects.create_user("reader", password="test-only")
    client.force_login(user)
    assert client.post("/movements/create/", plan_data).status_code == 403
    assert client.post("/movements/1/cancel/").status_code == 403


def test_real_csrf_protection(admin_user, inventory_db, plan_data):
    client = Client(enforce_csrf_checks=True)
    client.force_login(admin_user)
    assert client.post("/movements/create/", plan_data).status_code == 403
    client.get("/movements/create/")
    token = client.cookies["csrftoken"].value
    assert (
        client.post(
            "/movements/create/", plan_data, HTTP_X_CSRFTOKEN=token
        ).status_code
        == 302
    )


@pytest.mark.parametrize(
    "path",
    [
        "/movements/999/edit/",
        "/movements/999/cancel/",
        "/movements/999/complete/",
        "/items/999/edit/",
    ],
)
def test_missing_objects(admin_client, inventory_db, path):
    assert admin_client.post(path, {}).status_code == 404


def test_forms_filter_errors_and_statuses(client, inventory_db):
    for values in (
        {"date": "bad"},
        {"room": 999},
        {"sort": "sql"},
        {"item": "bad"},
    ):
        response = client.get("/movements/", values)
        assert response.status_code == 400
        assert response.context["form"].errors
    response = client.get("/movements/", {"status": "COMPLETED"})
    assert len(response.context["entries"]) == 2
    assert (
        len(
            client.get("/movements/", {"status": "PLANNED"}).context["entries"]
        )
        == 0
    )


def test_filter_pagination_keeps_all_values(client, inventory_db):
    template = Movement.objects.completed().first()
    for n in range(25):
        Movement.objects.create(
            item=template.item,
            source=template.source,
            target=template.target,
            status="COMPLETED",
            scheduled_for=timezone.localdate(),
        )
    response = client.get(
        "/movements/",
        {
            "status": "COMPLETED",
            "sort": "oldest",
            "room": template.source_id,
            "q": template.item.name,
        },
    )
    link = response.context["following"]
    assert "sort=oldest" in link and "status=COMPLETED" in link
    assert "room=" in link and "q=" in link and "page=2" in link


def test_upload_item_and_disabled_room(
    admin_client, inventory_db, settings, tmp_path
):
    settings.MEDIA_ROOT = tmp_path
    stream = BytesIO()
    Image.new("RGB", (64, 64), "#228866").save(stream, "PNG")
    upload = SimpleUploadedFile(
        "item.png", stream.getvalue(), content_type="image/png"
    )
    values = dict(
        name="Ковш",
        category=1,
        condition=1,
        room=1,
        quantity=2,
        unit_price=10000,
    )
    response = admin_client.post("/items/create/", {**values, "image": upload})
    assert response.status_code == 302
    item = Item.objects.get(name="Ковш")
    assert item.image.storage.exists(item.image.name)
    assert item.image.url.encode() in admin_client.get(response.url).content
    response = admin_client.post(
        f"/items/{item.pk}/edit/", {**values, "room": 3}
    )
    assert response.status_code == 302
    item.refresh_from_db()
    assert item.room_id == 1


def test_invalid_image_and_written_off_validation(admin_client, inventory_db):
    upload = SimpleUploadedFile(
        "fake.png", b"not an image", content_type="image/png"
    )
    values = dict(
        name="Плохой файл",
        category=1,
        condition=1,
        room=1,
        quantity=1,
        unit_price=100,
    )
    response = admin_client.post("/items/create/", {**values, "image": upload})
    assert "image" in response.context["form"].errors
    assert not Item.objects.filter(name="Плохой файл").exists()
    item = Item.objects.get(pk=5)
    response = admin_client.post(
        "/items/5/edit/", {**values, "name": item.name}
    )
    assert "condition" in response.context["form"].errors


def test_admin_create_plan_uses_validations(
    admin_client, inventory_db, plan_data
):
    response = admin_client.post(
        "/admin/movements/movement/add/", {**plan_data, "_save": "Сохранить"}
    )
    assert response.status_code == 302
    assert Movement.objects.active().count() == 1
    response = admin_client.post(
        "/admin/movements/movement/add/",
        {**plan_data, "target": 1, "_save": "Сохранить"},
    )
    assert response.status_code == 200
    assert Movement.objects.active().count() == 1
