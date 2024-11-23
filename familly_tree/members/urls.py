from django.urls import path

from . import views

app_name = "members"
urlpatterns = [
    path("", views.main, name="main"),
    path(f"{app_name}/", views.AllMembers.as_view(), name="members"),
    path(f"{app_name}/<int:pk>", views.Details.as_view(), name="details"),
    path(f"{app_name}/add/", views.AddNew.as_view(), name="add"),
    path(f"{app_name}/edit/<int:pk>", views.EditMember.as_view(), name="edit"),
    path(f"{app_name}/remove/<int:pk>", views.DeleteMember.as_view(), name="remove"),
    path(f"{app_name}/tree", views.TreeView.as_view(), name="tree"),
    path(
        "choose_child/<int:parent_id>/",
        views.ChooseChildView.as_view(),
        name="choose_child",
    ),
    path(
        "add_child/<int:parent_id>/<int:child_id>/",
        views.add_child_to_parent,
        name="add_child_to_parent",
    ),
    path(
        f"{app_name}/<int:member_id>/marriages/",
        views.MemberMarriagesView.as_view(),
        name="member_marriages",
    ),
    path(
        f"{app_name}/<int:member_id>/marry/",
        views.MarryMemberCreateView.as_view(),
        name="marry_member_form",
    ),
    path(
        f"{app_name}/<int:member_id>/marry/<int:spouse_id>/",
        views.marry_member,
        name="marry_member",
    ),
    path(
        f"{app_name}/<int:member_id>/divorce/<int:spouse_id>/",
        views.divorce_member,
        name="divorce_member",
    ),
]
