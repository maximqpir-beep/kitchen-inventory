from django.urls import path

from . import views

app_name = "items"
urlpatterns = [
    path("create/", views.create, name="create"),
    path("<int:item_id>/edit/", views.edit, name="edit"),
    path("", views.item_list, name="list"),
    path("available/", views.available, name="available"),
    path("<int:item_id>/", views.item_detail, name="detail"),
]
