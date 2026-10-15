"""Главный маршрутизатор проекта."""

from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("items/", include("items.urls")),
    path("movements/", include("movements.urls")),
]
handler404 = "homepage.views.page_not_found"
