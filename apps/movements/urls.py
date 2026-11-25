from django.urls import path

from . import views

app_name = "movements"
urlpatterns = [
    path("create/", views.create, name="create"),
    path("<int:movement_id>/edit/", views.edit, name="edit"),
    path("<int:movement_id>/cancel/", views.cancel, name="cancel"),
    path("<int:movement_id>/complete/", views.complete, name="complete"),
    path("", views.movement_list, name="list"),
    path("<int:movement_id>/", views.movement_detail, name="detail"),
]
