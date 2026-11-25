"""Главный маршрутизатор проекта."""

from django.urls import include, path
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("items/", include("items.urls")),
    path("movements/", include("movements.urls")),
]
handler404 = "homepage.views.page_not_found"

admin.site.site_header = "Кухонный учет — управление"
admin.site.site_title = "Администрирование"
admin.site.index_title = "Инвентарь и перемещения"
if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
