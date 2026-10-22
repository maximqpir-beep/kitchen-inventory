"""Веб-часть ПР7 читает только SQLite; JSON остается в консоли ПР3."""

from django.conf import settings
from django.http import Http404

from db.database import DataUnavailable, fetch_all, fetch_one  # noqa: F401


def rows(name, parameters=()):
    return fetch_all(name, parameters, path=settings.DATABASE_PATH)


def row(name, parameters=()):
    return fetch_one(name, parameters, path=settings.DATABASE_PATH)


def row_or_404(name, identifier):
    result = row(name, (identifier,))
    if result is None:
        raise Http404("Запись не найдена.")
    return result


def search_pattern(text):
    """Поиск кириллицы без регистра; %, _ и слеш - обычные символы."""
    text = text.casefold().replace("\\", "\\\\")
    return "%" + text.replace("%", "\\%").replace("_", "\\_") + "%"
