"""Формы фильтрации, создание, редактирование и POST-действия."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import (
    require_http_methods,
    require_POST,
    require_safe,
)

from kitchen_site import orm
from .forms import MovementFilterForm, MovementForm
from .models import Movement
from .services import cancel_movement, complete_movement, save_plan


@require_safe
def movement_list(request):
    params = request.GET.copy()
    aliases = {"-1": "all", "0": "COMPLETED", "1": "CANCELLED", "2": "PLANNED"}
    if params.get("status") in aliases:
        params["status"] = aliases[params["status"]]
    form = MovementFilterForm(params)
    entries = orm.movement_list()
    valid = form.is_valid()
    if valid:
        data = form.cleaned_data
        if data["date"]:
            entries = entries.for_date(data["date"])
        status = data["status"] or "all"
        if status == "PLANNED":
            entries = entries.active()
        elif status == "COMPLETED":
            entries = entries.completed()
        elif status == "CANCELLED":
            entries = entries.cancelled()
        if data["room"]:
            entries = entries.filter(
                Q(source=data["room"]) | Q(target=data["room"])
            )
        if data["item"]:
            entries = entries.filter(item=data["item"])
        if data["q"]:
            query = data["q"].casefold()
            entries = entries.filter(
                Q(item__name_search__contains=query)
                | Q(target__name_search__contains=query)
            )
        allowed = {
            "newest": ("-scheduled_for", "-pk"),
            "oldest": ("scheduled_for", "pk"),
            "item": ("item__name_search", "pk"),
        }
        entries = entries.order_by(*allowed[data["sort"] or "newest"])
    else:
        entries = entries.none()
    context = orm.paginate(request, entries)
    context.update(
        entries=[
            {"movement": move, "created_at": move.created_at}
            for move in context["page_obj"]
        ],
        active="moves",
        form=form,
    )
    return render(
        request,
        "movements/movement_list.html",
        context,
        status=200 if valid else 400,
    )


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


def add_errors(form, error):
    if hasattr(error, "error_dict"):
        for field, errors in error.error_dict.items():
            form.add_error(field if field in form.fields else None, errors)
    else:
        form.add_error(None, error)


def edit_form(request, instance=None):
    if instance and instance.status != Movement.Status.PLANNED:
        return render(
            request,
            "400.html",
            {"error": "Редактировать можно только запланированную запись."},
            status=400,
        )
    form = MovementForm(
        request.POST if request.method == "POST" else None, instance=instance
    )
    if request.method == "POST" and form.is_valid():
        try:
            move = save_plan(form.save(commit=False))
        except ValidationError as error:
            add_errors(form, error)
        except IntegrityError:
            form.add_error(
                None, "План для этой партии на выбранную дату уже существует."
            )
        else:
            messages.success(request, "План перемещения сохранен.")
            return redirect(move)
    return render(
        request,
        "movements/movement_form.html",
        {
            "form": form,
            "movement": instance,
            "active": "moves",
        },
    )


@login_required
@permission_required("movements.add_movement", raise_exception=True)
@require_http_methods(["GET", "POST"])
def create(request):
    return edit_form(request)


@login_required
@permission_required("movements.change_movement", raise_exception=True)
@require_http_methods(["GET", "POST"])
def edit(request, movement_id):
    return edit_form(request, get_object_or_404(Movement, pk=movement_id))


def change_status(request, movement_id, operation):
    get_object_or_404(Movement, pk=movement_id)
    try:
        operation(movement_id)
    except ValidationError as error:
        messages.error(request, "; ".join(error.messages))
    else:
        messages.success(request, "Статус перемещения изменен.")
    return redirect("movements:detail", movement_id=movement_id)


@login_required
@permission_required("movements.change_movement", raise_exception=True)
@require_POST
def cancel(request, movement_id):
    return change_status(request, movement_id, cancel_movement)


@login_required
@permission_required("movements.change_movement", raise_exception=True)
@require_POST
def complete(request, movement_id):
    return change_status(request, movement_id, complete_movement)
