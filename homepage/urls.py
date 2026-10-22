from django.urls import path

from . import views

app_name = "homepage"
urlpatterns = [
    path("", views.index, name="index"),
    path("statistics/", views.statistics, name="statistics"),
    path("rooms/", views.rooms_list, name="rooms"),
]
