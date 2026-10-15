"""Каркас HTML для ПР5; в ПР6 заменяется шаблонами."""

from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html, format_html_join


def money(cents: int) -> str:
    return f"{cents // 100:,}.{cents % 100:02d}".replace(",", " ")


def page(title: str, body, active: str = "home"):
    """Безопасно подставить данные в общий каркас документа."""
    links = format_html_join("", '<a class="{}" href="{}">{}</a>', (
        ("current" if key == active else "", reverse(route), label)
        for key, route, label in (
            ("home", "homepage:index", "Обзор"),
            ("items", "items:list", "Инвентарь"),
            ("moves", "movements:list", "Перемещения"),
        )
    ))
    return format_html(
        '<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>{} · Кухонный учет</title>'
        '<link rel="stylesheet" href="{}">'
        '<link rel="stylesheet" href="{}"></head><body>'
        '<header class="site-header"><div class="shell header-inner">'
        '<a class="brand" href="{}"><span class="brand-mark">К</span>'
        'Кухонный учет</a><nav aria-label="Главная навигация">{}</nav>'
        '<span class="group-label">ЭФБО-12-24</span></div></header>'
        '<main class="shell main-content" id="main">{}</main>'
        '<footer class="shell site-footer">Учет предметов, состояний и '
        'помещений кухни</footer></body></html>',
        title, static("homepage/vendor/bootstrap.min.css"),
        static("homepage/css/style.css"), reverse("homepage:index"),
        links, body,
    )


def state_badge(item):
    kind = "good" if item.condition.id == 1 else "warn"
    if item.condition.id == 3:
        kind = "muted"
    return format_html('<span class="status {}">{}</span>',
                       kind, item.condition.name)


def item_card(item):
    return format_html(
        '<article class="inventory-card card"><div class="card-body">'
        '<div class="card-top"><span class="eyebrow">№ {}</span>'
        '{}</div><h2 class="card-title">{}</h2>'
        '<p class="category">{}</p><dl class="card-facts">'
        '<div><dt>Помещение</dt><dd>{}</dd></div>'
        '<div><dt>Количество</dt><dd>{} шт.</dd></div></dl>'
        '<div class="card-bottom"><strong>{} ₽</strong>'
        '<a href="{}">Подробнее →</a></div></div></article>',
        f"{item.id:03d}", state_badge(item), item.name, item.category.name,
        item.room.name, item.quantity, money(item.total),
        reverse("items:detail", args=[item.id]),
    )


def movement_badge(movement):
    return format_html('<span class="status {}">{}</span>',
                       "muted" if movement.cancelled else "good",
                       "Отменено" if movement.cancelled else "Выполнено")
