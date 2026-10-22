"""Каталог, фильтры и карточка получают именованные строки SQLite."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from kitchen_site.parameters import integer
from kitchen_site.source import row_or_404, rows, search_pattern


@require_safe
def item_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    try:
        room_id = integer(request, "room")
        state_id = integer(request, "state")
        category_id = integer(request, "category")
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    return render(request, "items/item_list.html", {
        "items": rows("items", (search_pattern(query), room_id, room_id,
                                state_id, state_id, category_id,
                                category_id)),
        "query": query, "active": "items", "room_id": room_id,
        "state_id": state_id, "category_id": category_id,
        "rooms": rows("rooms"), "categories": rows("categories"),
        "conditions": rows("conditions"),
    })


@require_safe
def available(request: HttpRequest) -> HttpResponse:
    try:
        room_id = integer(request, "room")
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    return render(request, "items/available.html", {
        "items": rows("available_items", (room_id, room_id)),
        "rooms": rows("rooms"), "room_id": room_id, "active": "items",
    })


@require_safe
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    return render(request, "items/item_detail.html", {
        "item": row_or_404("item_detail", item_id), "active": "items",
    })
