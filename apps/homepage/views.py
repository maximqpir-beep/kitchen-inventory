"""Обзор, помещения и статистика через ORM."""

from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from apps.items.models import Room
from config import orm
from config.parameters import integer


@require_safe
def index(request):
    return render(
        request,
        "homepage/index.html",
        {
            "stats": orm.totals(),
            "active": "home",
            "expensive": orm.item_list().order_by("-cost", "pk")[:3],
        },
    )


@require_safe
def statistics(request):
    try:
        threshold = integer(request, "min_units", default=2)
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    context = orm.statistics(threshold)
    context.update(threshold=threshold, active="stats")
    return render(request, "homepage/statistics.html", context)


@require_safe
def rooms_list(request):
    return render(
        request,
        "homepage/rooms.html",
        {
            "rooms": Room.objects.all(),
            "active": "rooms",
        },
    )


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def data_unavailable(request):
    return render(request, "503.html", status=503)


@require_safe
def room_detail(request, slug):
    room = get_object_or_404(
        Room.objects.prefetch_related(
            "items__category", "items__condition", "items__room"
        ),
        slug=slug,
    )
    return render(
        request,
        "homepage/room_detail.html",
        {
            "room": room,
            "items": room.items.all(),
            "active": "rooms",
        },
    )
