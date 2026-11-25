"""Единые правила для Admin и пользовательских форм, атомарные изменения."""

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.items.models import Item
from .models import Movement


@transaction.atomic
def save_plan(candidate):
    item = (
        Item.objects.select_for_update()
        .select_related("condition")
        .get(pk=candidate.item_id)
    )
    if candidate.pk:
        existing = Movement.objects.select_for_update().get(pk=candidate.pk)
        if existing.status != Movement.Status.PLANNED:
            raise ValidationError(
                "Редактировать можно только запланированную запись."
            )
    candidate.item = item
    candidate.source_id = item.room_id
    candidate.status = Movement.Status.PLANNED
    candidate.full_clean()
    candidate.save()
    return candidate


@transaction.atomic
def complete_movement(pk):
    move = Movement.objects.select_for_update().with_related().get(pk=pk)
    if move.status != Movement.Status.PLANNED:
        raise ValidationError(
            "Выполнить можно только запланированное перемещение."
        )
    if move.scheduled_for > timezone.localdate():
        raise ValidationError("Дата перемещения еще не наступила.")
    updated = Item.objects.filter(
        pk=move.item_id, room_id=move.source_id, condition__usable=True
    ).update(room_id=move.target_id)
    if updated != 1:
        raise ValidationError(
            "Предмет неисправен или его помещение изменилось."
        )
    move.status = Movement.Status.COMPLETED
    move.executed_at = timezone.now()
    move.save(update_fields=["status", "executed_at"])
    return move


@transaction.atomic
def cancel_movement(pk):
    move = Movement.objects.select_for_update().with_related().get(pk=pk)
    if move.status == Movement.Status.CANCELLED:
        raise ValidationError("Запись уже отменена.")
    if move.status == Movement.Status.COMPLETED:
        later = (
            Movement.objects.completed()
            .filter(item_id=move.item_id)
            .exclude(pk=move.pk)
            .filter(models_after(move))
        )
        if later.exists():
            raise ValidationError(
                "Сначала отмените более позднее перемещение."
            )
        if (
            Item.objects.filter(
                pk=move.item_id, room_id=move.target_id
            ).update(room_id=move.source_id)
            != 1
        ):
            raise ValidationError("Текущее помещение не совпадает с записью.")
    move.status = Movement.Status.CANCELLED
    move.save(update_fields=["status"])
    return move


def models_after(move):
    from django.db.models import Q

    return Q(executed_at__gt=move.executed_at) | Q(
        executed_at=move.executed_at, pk__gt=move.pk
    )
