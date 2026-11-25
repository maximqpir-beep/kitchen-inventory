"""Главный маршрутизатор проекта."""

from django.urls import include, path
from django.contrib import admin
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.homepage.urls")),
    path("items/", include("apps.items.urls")),
    path("movements/", include("apps.movements.urls")),
]
handler404 = "apps.homepage.views.page_not_found"

admin.site.site_header = "Кухонный учет — управление"
admin.site.site_title = "Администрирование"
admin.site.index_title = "Инвентарь и перемещения"
if "debug_toolbar" in settings.INSTALLED_APPS:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
