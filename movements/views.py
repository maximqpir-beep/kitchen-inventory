"""Даты подготавливаются во view, оформление вынесено в шаблоны."""

from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from kitchen_site.source import find_movement_or_404, read_inventory


@require_safe
def movement_list(request: HttpRequest) -> HttpResponse:
    entries = [{"movement": movement,
                "created_at": datetime.fromisoformat(movement.created_at)}
               for movement in reversed(read_inventory()["moves"])]
    return render(request, "movements/movement_list.html", {
        "entries": entries, "active": "moves",
    })


@require_safe
def movement_detail(request: HttpRequest,
                    movement_id: int) -> HttpResponse:
    move = find_movement_or_404(read_inventory(), movement_id)
    return render(request, "movements/movement_detail.html", {
        "movement": move,
        "created_at": datetime.fromisoformat(move.created_at),
        "active": "moves",
    })
