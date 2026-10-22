"""SQL JOIN, фильтр даты и статуса, стабильная постраничная выборка."""

from datetime import datetime
from urllib.parse import urlencode

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from kitchen_site.parameters import integer, selected_date
from kitchen_site.source import row_or_404, rows

PAGE_SIZE = 20


@require_safe
def movement_list(request: HttpRequest) -> HttpResponse:
    try:
        date = selected_date(request)
        status = integer(request, "status", default=-1, minimum=-1,
                         maximum=1)
        page = integer(request, "page", default=1, minimum=1)
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    found = rows("movements", (date, date, status, status, PAGE_SIZE + 1,
                               (page - 1) * PAGE_SIZE))
    entries = [{"movement": movement,
                "created_at": datetime.fromisoformat(movement["created_at"])}
               for movement in found[:PAGE_SIZE]]
    previous = urlencode({"date": date, "status": status, "page": page - 1})
    following = urlencode({"date": date, "status": status, "page": page + 1})
    return render(request, "movements/movement_list.html", {
        "entries": entries, "active": "moves", "date": date,
        "status": status, "page": page,
        "previous": previous if page > 1 else None,
        "following": following if len(found) > PAGE_SIZE else None,
    })


@require_safe
def movement_detail(request: HttpRequest,
                    movement_id: int) -> HttpResponse:
    move = row_or_404("movement_detail", movement_id)
    return render(request, "movements/movement_detail.html", {
        "movement": move,
        "created_at": datetime.fromisoformat(move["created_at"]),
        "active": "moves",
    })
