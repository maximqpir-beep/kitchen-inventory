from django.urls import path

from . import views

app_name = "movements"
urlpatterns = [
    path("", views.movement_list, name="list"),
    path("<int:movement_id>/", views.movement_detail, name="detail"),
]
