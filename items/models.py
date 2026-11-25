"""Модели ПР9; классы старой консоли остаются в models/."""

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
from django.urls import reverse


class NamedModel(models.Model):
    name = models.CharField("Название", max_length=160, unique=True)
    name_search = models.CharField(max_length=200, editable=False)

    class Meta:
        abstract = True
        ordering = ("name", "pk")

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name_search = self.name.casefold()
        if kwargs.get("update_fields"):
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {
                "name_search"
            }
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(NamedModel):
    class Meta(NamedModel.Meta):
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Condition(NamedModel):
    usable = models.BooleanField("Пригоден к использованию", default=False)

    class Meta(NamedModel.Meta):
        verbose_name = "Состояние"
        verbose_name_plural = "Состояния"


class Room(NamedModel):
    description = models.TextField("Описание", blank=True, default="")

    class Meta(NamedModel.Meta):
        verbose_name = "Помещение"
        verbose_name_plural = "Помещения"


class ItemQuerySet(models.QuerySet):
    def with_related(self):
        return self.select_related("category", "condition", "room")

    def with_cost(self):
        return self.annotate(cost=F("quantity") * F("unit_price"))

    def usable(self):
        return self.filter(condition__usable=True)


class Item(models.Model):
    name = models.CharField("Название", max_length=160)
    name_search = models.CharField(max_length=200, editable=False)
    category = models.ForeignKey(
        Category,
        models.PROTECT,
        related_name="items",
        verbose_name="Категория",
    )
    condition = models.ForeignKey(
        Condition,
        models.PROTECT,
        related_name="items",
        verbose_name="Состояние",
    )
    room = models.ForeignKey(
        Room, models.PROTECT, related_name="items", verbose_name="Помещение"
    )
    quantity = models.PositiveIntegerField(
        "Количество", default=1, validators=[MinValueValidator(1)]
    )
    unit_price = models.PositiveBigIntegerField(
        "Цена, коп.", validators=[MinValueValidator(1)]
    )
    objects = ItemQuerySet.as_manager()

    class Meta:
        ordering = ("name_search", "pk")
        verbose_name = "Предмет"
        verbose_name_plural = "Инвентарь"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="item_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(unit_price__gt=0),
                name="item_price_positive",
            ),
        ]

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name_search = self.name.casefold()
        if kwargs.get("update_fields"):
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {
                "name_search"
            }
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("items:detail", args=[self.pk])

    @property
    def total(self):
        return self.quantity * self.unit_price

    @property
    def category_name(self):
        return self.category.name

    @property
    def room_name(self):
        return self.room.name

    @property
    def state_id(self):
        return self.condition_id

    @property
    def state_name(self):
        return self.condition.name

    @property
    def usable(self):
        return self.condition.usable
