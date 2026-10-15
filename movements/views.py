"""История и карточка перемещения, без записи данных через HTTP."""

from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_safe

from homepage.html import movement_badge, page
from kitchen_site.source import find_movement_or_404, read_inventory


def display_date(value: str) -> str:
    return datetime.fromisoformat(value).strftime("%d.%m.%Y %H:%M")


@require_safe
def movement_list(request: HttpRequest) -> HttpResponse:
    moves = list(reversed(read_inventory()["moves"]))
    rows = format_html_join("", (
        '<tr><td><a href="{}">№ {}</a></td><td>{}</td>'
        '<td>{} → {}</td><td>{}</td><td>{}</td></tr>'
    ), ((reverse("movements:detail", args=[m.id]), m.id, m.item.name,
         m.source.name, m.target.name, display_date(m.created_at),
         movement_badge(m)) for m in moves))
    if not moves:
        rows = format_html('<tr><td colspan="5">{}</td></tr>',
                           "Перемещений пока нет.")
    body = format_html(
        '<p class="eyebrow">02 / ИСТОРИЯ</p><h1>Перемещения</h1>'
        '<p class="subtitle">Откуда, куда и когда перемещался инвентарь.</p>'
        '<div class="table-panel table-responsive"><table class="table">'
        '<thead><tr><th>Запись</th><th>Предмет</th><th>Маршрут</th>'
        '<th>Дата</th><th>Статус</th></tr></thead><tbody>{}</tbody>'
        '</table></div><p class="quiet-note">Отмененные записи остаются '
        'в истории. Новые записи показаны первыми.</p>', rows,
    )
    return HttpResponse(page("Перемещения", body, "moves"))


@require_safe
def movement_detail(request: HttpRequest,
                    movement_id: int) -> HttpResponse:
    move = find_movement_or_404(read_inventory(), movement_id)
    note = ("Запись отменена и не участвует в текущей цепочке перемещений."
            if move.cancelled else "Перемещение выполнено.")
    body = format_html(
        '<a class="back-link" href="{}">← Все перемещения</a>'
        '<section class="detail-panel"><p class="eyebrow">ЗАПИСЬ № {}</p>'
        '<div class="section-header"><h1>Перемещение инвентаря</h1>{}</div>'
        '<p class="subtitle">{}</p><div class="route-panel">'
        '<div><span>Откуда</span><strong>{}</strong></div>'
        '<span aria-hidden="true">→</span>'
        '<div><span>Куда</span><strong>{}</strong></div></div>'
        '<p>{}</p><p>Предмет: <a href="{}">{}</a></p>'
        '<p class="quiet-note">{}</p></section>',
        reverse("movements:list"), move.id, movement_badge(move),
        display_date(move.created_at), move.source.name, move.target.name,
        note, reverse("items:detail", args=[move.item.id]), move.item.name,
        "Маршрут записи не обязательно совпадает с текущим помещением "
        "предмета: после нее могли быть другие операции.",
    )
    return HttpResponse(page(f"Перемещение № {move.id}", body, "moves"))
