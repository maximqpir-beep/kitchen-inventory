"""Представления готовят объекты и контекст, но не HTML-строки."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from kitchen_site.source import (
    find_item_or_404, read_inventory, select_items,
)


@require_safe
def item_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    return render(request, "items/item_list.html", {
        "items": select_items(read_inventory(), query),
        "query": query, "active": "items",
    })


@require_safe
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    return render(request, "items/item_detail.html", {
        "item": find_item_or_404(read_inventory(), item_id),
        "active": "items",
    })
