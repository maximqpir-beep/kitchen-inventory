"""История перемещений инвентаря в Django ORM."""
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Movement(models.Model):
    item = models.ForeignKey("items.Item", models.PROTECT,
                             related_name="movements", verbose_name="Предмет")
    source = models.ForeignKey("items.Room", models.PROTECT,
                               related_name="outgoing", verbose_name="Откуда")
    target = models.ForeignKey("items.Room", models.PROTECT,
                               related_name="incoming", verbose_name="Куда")
    created_at = models.DateTimeField("Создано", default=timezone.now)
    cancelled = models.BooleanField("Отменено", default=False)

    class Meta:
        ordering = ("-created_at", "-pk")
        verbose_name = "Перемещение"
        verbose_name_plural = "Перемещения"
        constraints = [models.CheckConstraint(
            condition=~models.Q(source=models.F("target")),
            name="movement_different_rooms",
        )]

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
