from django.urls import path

from . import views

app_name = "members"
urlpatterns = [
    path("", views.main, name="main"),
    path("members/", views.members, name="members"),
    path("members/details/<int:id>", views.details, name="details"),
    path("members/add/", views.add_new, name="add"),
]
