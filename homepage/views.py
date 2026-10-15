"""Обзор и страницы ошибок через Django Templates."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe

from inventory import statistics
from kitchen_site.source import read_inventory


@require_safe
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "homepage/index.html", {
        "stats": statistics(read_inventory()), "active": "home",
    })


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def data_unavailable(request: HttpRequest) -> HttpResponse:
    return render(request, "503.html", status=503)
