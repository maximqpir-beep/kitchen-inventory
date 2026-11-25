"""Фильтрация истории и Paginator без загрузки всей коллекции."""

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from kitchen_site import orm
from kitchen_site.parameters import integer, selected_date


@require_safe
def movement_list(request):
    try:
        date = selected_date(request)
        status = integer(request, "status", default=-1, minimum=-1, maximum=1)
        integer(request, "page", default=1, minimum=1)
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    entries = orm.movement_list()
    if date:
        entries = entries.filter(created_at__date=date)
    if status != -1:
        entries = entries.filter(cancelled=bool(status))
    query = request.GET.get("q", "").strip()[:200]
    if query:
        entries = entries.filter(
            Q(item__name_search__contains=query.casefold())
            | Q(target__name_search__contains=query.casefold())
        )
    order = request.GET.get("sort", "newest")
    allowed = {
        "newest": ("-created_at", "-pk"),
        "oldest": ("created_at", "pk"),
        "item": ("item__name_search", "pk"),
    }
    if order not in allowed:
        return render(
            request, "400.html", {"error": "Неверная сортировка."}, status=400
        )
    context = orm.paginate(request, entries.order_by(*allowed[order]))
    context.update(
        entries=[
            {"movement": move, "created_at": move.created_at}
            for move in context["page_obj"]
        ],
        active="moves",
        date=date,
        status=status,
        query=query,
        sort=order,
    )
    return render(request, "movements/movement_list.html", context)


@require_safe
def movement_detail(request, movement_id):
    move = get_object_or_404(orm.movement_list(), pk=movement_id)
    return render(
        request,
        "movements/movement_detail.html",
        {
            "movement": move,
            "created_at": move.created_at,
            "active": "moves",
        },
    )
