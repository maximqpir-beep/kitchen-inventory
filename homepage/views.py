"""Обзор и статистика формируются SQL-агрегатами."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from kitchen_site.parameters import integer
from kitchen_site.source import row, rows


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "homepage/index.html", {
        "stats": row("inventory_totals"), "active": "home",
        "expensive": rows("expensive_items", (3, 0)),
    })


@require_safe
def statistics(request: HttpRequest) -> HttpResponse:
    try:
        threshold = integer(request, "min_units", default=2)
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    return render(request, "homepage/statistics.html", {
        "stats": row("inventory_totals"),
        "moves": row("movement_totals"), "prices": row("price_bounds"),
        "categories": rows("category_statistics"),
        "rooms": rows("room_statistics"),
        "conditions": rows("condition_statistics"),
        "heavy_rooms": rows("heavy_rooms", (threshold,)),
        "threshold": threshold, "active": "stats",
    })


@require_safe
def rooms_list(request: HttpRequest) -> HttpResponse:
    return render(request, "homepage/rooms.html", {
        "rooms": rows("rooms"), "active": "rooms",
    })


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def data_unavailable(request: HttpRequest) -> HttpResponse:
    return render(request, "503.html", status=503)
