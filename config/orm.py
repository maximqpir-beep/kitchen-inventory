"""Повторно используемые ORM-запросы для представлений ПР9."""

from django.core.paginator import Paginator
from django.db.models import Avg, BigIntegerField, Count, F, Max, Min, Q, Sum
from django.db.models.functions import Cast, Coalesce, Round

from apps.items.models import Category, Condition, Item, Room
from apps.movements.models import Movement


def item_list():
    return Item.objects.with_related().with_cost()


def movement_list():
    return Movement.objects.with_related()


def totals():
    return Item.objects.aggregate(
        batches=Count("pk"),
        units=Coalesce(Sum("quantity"), 0),
        total=Coalesce(
            Sum(F("quantity") * F("unit_price")),
            0,
            output_field=BigIntegerField(),
        ),
        usable=Coalesce(Sum("quantity", filter=Q(condition__usable=True)), 0),
    )


def grouped(model, *, total=True):
    fields = dict(
        batches=Count("items"), units=Coalesce(Sum("items__quantity"), 0)
    )
    if total:
        fields["total"] = Coalesce(
            Sum(F("items__quantity") * F("items__unit_price")),
            0,
            output_field=BigIntegerField(),
        )
    return model.objects.values("id", "name").annotate(**fields).order_by("id")


def statistics(threshold):
    return {
        "stats": totals(),
        "moves": Movement.objects.aggregate(
            total=Count("pk"),
            done=Count("pk", filter=Q(status="COMPLETED")),
            planned=Count("pk", filter=Q(status="PLANNED")),
            cancelled=Count("pk", filter=Q(status="CANCELLED")),
        ),
        "prices": Item.objects.aggregate(
            minimum=Min("unit_price"),
            maximum=Max("unit_price"),
            average=Cast(Round(Avg("unit_price")), BigIntegerField()),
        ),
        "categories": grouped(Category),
        "rooms": grouped(Room),
        "conditions": grouped(Condition, total=False),
        "heavy_rooms": grouped(Room, total=False).filter(units__gte=threshold),
    }


def paginate(request, queryset, *, per_page=20):
    from urllib.parse import urlencode

    page = Paginator(queryset, per_page).get_page(request.GET.get("page", 1))
    params = request.GET.copy()
    params.pop("page", None)

    def link(number):
        return urlencode({**params.dict(), "page": number})

    return {
        "page_obj": page,
        "page": page.number,
        "previous": (
            link(page.previous_page_number()) if page.has_previous() else None
        ),
        "following": (
            link(page.next_page_number()) if page.has_next() else None
        ),
    }
