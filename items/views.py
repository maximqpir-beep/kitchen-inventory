"""Список и карточка инвентаря: исходные объекты ПР3."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.views.decorators.http import require_safe

from homepage.html import item_card, money, page, state_badge
from kitchen_site.source import (
    find_item_or_404, read_inventory, select_items,
)


@require_safe
def item_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    items = select_items(read_inventory(), query)
    cards = format_html_join("", "{}", ((item_card(i),) for i in items))
    if not items:
        cards = format_html(
            '<div class="empty-state"><h2>Предметы не найдены</h2>'
            '<p>Попробуйте другой запрос или откройте весь каталог.</p>'
            '<a href="{}">Сбросить поиск</a></div>', reverse("items:list"),
        )
    body = format_html(
        '<p class="eyebrow">01 / КАТАЛОГ</p><div class="section-header">'
        '<div><h1>Кухонный инвентарь</h1><p class="subtitle">'
        'Состояние и расположение каждой партии.</p></div>'
        '<span class="count">Найдено: {}</span></div>'
        '<form class="search-bar" method="get" action="{}">'
        '<label for="q">Поиск по названию</label><div class="search-row">'
        '<input id="q" name="q" value="{}" placeholder="Например, нож" '
        'class="form-control"><button class="btn btn-primary">Найти</button>'
        '</div></form><div class="inventory-grid">{}</div>',
        len(items), reverse("items:list"), query, cards,
    )
    return HttpResponse(page("Инвентарь", body, "items"))


@require_safe
def item_detail(request: HttpRequest, item_id: int) -> HttpResponse:
    item = find_item_or_404(read_inventory(), item_id)
    body = format_html(
        '<a class="back-link" href="{}">← Весь инвентарь</a>'
        '<section class="detail-panel"><p class="eyebrow">ПРЕДМЕТ № {}</p>'
        '<div class="section-header"><h1>{}</h1>{}</div>'
        '<p class="subtitle">{}</p><dl class="detail-facts">'
        '<div><dt>Помещение</dt><dd>{}</dd></div>'
        '<div><dt>Количество</dt><dd>{} шт.</dd></div>'
        '<div><dt>Цена за штуку</dt><dd>{} ₽</dd></div>'
        '<div><dt>Стоимость партии</dt><dd>{} ₽</dd></div></dl>'
        '<div class="usage-note"><strong>{}</strong><p>{}</p></div>'
        '</section>', reverse("items:list"), item.id, item.name,
        state_badge(item), item.category.name, item.room.name, item.quantity,
        money(item.unit_price), money(item.total), item.usage_status(),
        item.handling_note(),
    )
    return HttpResponse(page(item.name, body, "items"))
