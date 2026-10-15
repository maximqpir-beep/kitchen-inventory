"""Главная и страницы ошибок: HTML через HttpResponse в ПР5."""

from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_safe

from inventory import statistics
from kitchen_site.source import read_inventory
from .html import money, page


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    data = read_inventory()
    stats = statistics(data)
    body = format_html(
        '<section class="hero"><div><p class="eyebrow">КУХНЯ ПОД КОНТРОЛЕМ</p>'
        '<h1>Все на своем месте.</h1><p class="lead">Предметы, состояния и '
        'перемещения — в одном месте. Быстро найдите нужный инвентарь.</p>'
        '<a class="btn btn-primary" href="{}">Открыть инвентарь →</a>'
        '</div><div class="hero-note"><span>01 / ОБЗОР</span>'
        '<strong>Порядок начинается<br>с учета.</strong></div></section>'
        '<section class="stats" aria-label="Статистика">'
        '<div><span>Партий инвентаря</span><strong>{}</strong></div>'
        '<div><span>Предметов всего</span><strong>{}</strong></div>'
        '<div><span>Исправных предметов</span><strong>{}</strong></div>'
        '<div><span>Общая стоимость</span><strong>{} ₽</strong></div>'
        '</section><section class="section-header"><div>'
        '<p class="eyebrow">РАБОТА С ИНВЕНТАРЕМ</p>'
        '<h2>Два раздела для ежедневного учета</h2></div></section>'
        '<div class="feature-grid">'
        '<a class="feature-card" href="{}">'
        '<span class="eyebrow">01 / ПРЕДМЕТЫ</span>'
        '<h3>Каталог инвентаря →</h3>'
        '<p>Проверьте состояние, количество и место хранения.</p></a>'
        '<a class="feature-card" href="{}"><span class="eyebrow">'
        '02 / ИСТОРИЯ</span><h3>Перемещения →</h3>'
        '<p>Посмотрите маршруты предметов и отмененные записи.</p></a></div>'
        '<p class="quiet-note">На сайте доступен просмотр. Добавление и '
        'изменение данных выполняются через консольное меню main.py.</p>',
        reverse("items:list"), stats["batches"], stats["units"],
        stats["usable"], money(stats["total"]), reverse("items:list"),
        reverse("movements:list"),
    )
    return HttpResponse(page("Обзор", body))


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    body = format_html(
        '<section class="error-panel"><p class="eyebrow">ОШИБКА 404</p>'
        '<h1>Страница не найдена</h1><p>Проверьте адрес или выберите '
        'предмет из каталога.</p><a class="btn btn-primary" href="{}">'
        'На главную</a></section>', reverse("homepage:index"),
    )
    return HttpResponse(page("Страница не найдена", body), status=404)


def data_unavailable(request: HttpRequest) -> HttpResponse:
    body = format_html(
        '<section class="error-panel"><p class="eyebrow">ОШИБКА 503</p>'
        '<h1>Данные временно недоступны</h1><p>Проверьте файл '
        'data/inventory.json. Его содержимое не изменено.</p>'
        '<a class="btn btn-primary" href="{}">Повторить</a></section>',
        reverse("homepage:index"),
    )
    return HttpResponse(page("Данные недоступны", body), status=503)
