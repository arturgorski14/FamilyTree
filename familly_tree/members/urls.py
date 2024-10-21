from django.urls import path

from . import views

app_name = "members"
urlpatterns = [
    path("", views.main, name="main"),
    path(f"{app_name}/", views.members, name="members"),
    path(f"{app_name}/details/<int:pk>", views.details, name="details"),
    path(f"{app_name}/add/", views.add_new, name="add"),
    path(f"{app_name}/edit/<int:pk>", views.edit, name="edit"),
    path(f"{app_name}/remove/<int:pk>", views.remove, name="remove"),
]
