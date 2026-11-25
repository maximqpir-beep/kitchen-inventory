"""Статусы, менеджер и проверки перемещений (ПР10)."""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class MovementQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status="PLANNED")

    def cancelled(self):
        return self.filter(status="CANCELLED")

    def completed(self):
        return self.filter(status="COMPLETED")

    def for_date(self, date):
        return self.filter(scheduled_for=date)

    def with_related(self):
        return self.select_related("item", "source", "target")


class Movement(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Запланировано"
        COMPLETED = "COMPLETED", "Выполнено"
        CANCELLED = "CANCELLED", "Отменено"

    item = models.ForeignKey(
        "items.Item",
        models.PROTECT,
        related_name="movements",
        verbose_name="Предмет",
    )
    source = models.ForeignKey(
        "items.Room",
        models.PROTECT,
        related_name="outgoing",
        verbose_name="Откуда",
    )
    target = models.ForeignKey(
        "items.Room",
        models.PROTECT,
        related_name="incoming",
        verbose_name="Куда",
    )
    created_at = models.DateTimeField("Создано", default=timezone.now)
    scheduled_for = models.DateField(
        "Дата перемещения", default=timezone.localdate
    )
    executed_at = models.DateTimeField("Выполнено в", blank=True, null=True)
    status = models.CharField(
        "Статус", max_length=12, choices=Status.choices, default=Status.PLANNED
    )
    note = models.TextField("Примечание", blank=True, max_length=2000)
    objects = MovementQuerySet.as_manager()

    class Meta:
        ordering = ("-scheduled_for", "-created_at", "-pk")
        verbose_name = "Перемещение"
        verbose_name_plural = "Перемещения"
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(source=models.F("target")),
                name="movement_different_rooms",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["PLANNED", "COMPLETED", "CANCELLED"]
                ),
                name="movement_valid_status",
            ),
            models.UniqueConstraint(
                fields=["item", "scheduled_for"],
                condition=models.Q(status="PLANNED"),
                name="one_item_plan_per_day",
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}
        if self.source_id and self.source_id == self.target_id:
            errors["target"] = "Выберите другое помещение."
        if self.status == self.Status.PLANNED:
            if (
                self.scheduled_for
                and self.scheduled_for < timezone.localdate()
            ):
                errors["scheduled_for"] = (
                    "Нельзя планировать на прошедшую дату."
                )
            if self.item_id:
                if not self.item.condition.usable:
                    errors["item"] = "Предмет должен быть исправен."
                if self.source_id and self.source_id != self.item.room_id:
                    errors["target"] = (
                        "Помещение предмета изменилось; обновите форму."
                    )
                if (
                    self.scheduled_for
                    and type(self)
                    .objects.active()
                    .filter(
                        item_id=self.item_id, scheduled_for=self.scheduled_for
                    )
                    .exclude(pk=self.pk)
                    .exists()
                ):
                    errors["item"] = "На эту дату уже есть план для предмета."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"№ {self.pk}: {self.item}"

    def get_absolute_url(self):
        return reverse("movements:detail", args=[self.pk])

    @property
    def item_name(self):
        return self.item.name

    @property
    def source_name(self):
        return self.source.name

    @property
    def target_name(self):
        return self.target.name
