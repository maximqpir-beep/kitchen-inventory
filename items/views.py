"""Каталог, фильтры, поиск и связанные объекты Django ORM."""

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from kitchen_site import orm
from kitchen_site.parameters import integer
from .models import Category, Condition, Room


@require_safe
def item_list(request):
    query = request.GET.get("q", "").strip()[:200]
    try:
        room = integer(request, "room")
        state = integer(request, "state")
        category = integer(request, "category")
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    items = orm.item_list()
    if query:
        items = items.filter(
            Q(name_search__contains=query.casefold())
            | Q(category__name_search__contains=query.casefold())
        )
    for field, value in (
        ("room_id", room),
        ("condition_id", state),
        ("category_id", category),
    ):
        if value:
            items = items.filter(**{field: value})
    allowed = {"name": "name_search", "price": "-cost", "room": "room__name"}
    sort = request.GET.get("sort", "name")
    if sort not in allowed:
        return render(
            request, "400.html", {"error": "Неверная сортировка."}, status=400
        )
    context = orm.paginate(request, items.order_by(allowed[sort], "pk"))
    context.update(
        items=context["page_obj"].object_list,
        query=query,
        active="items",
        room_id=room,
        state_id=state,
        category_id=category,
        sort=sort,
        rooms=Room.objects.all(),
        categories=Category.objects.all(),
        conditions=Condition.objects.all(),
    )
    return render(request, "items/item_list.html", context)


@require_safe
def available(request):
    try:
        room = integer(request, "room")
    except ValueError as error:
        return render(request, "400.html", {"error": str(error)}, status=400)
    items = orm.item_list().exclude(condition__usable=False)
    if room:
        items = items.filter(room_id=room, condition__usable=True)
    return render(
        request,
        "items/available.html",
        {
            "items": items,
            "rooms": Room.objects.all(),
            "room_id": room,
            "active": "items",
        },
    )


@require_safe
def item_detail(request, item_id):
    return render(
        request,
        "items/item_detail.html",
        {
            "item": get_object_or_404(orm.item_list(), pk=item_id),
            "active": "items",
        },
    )
