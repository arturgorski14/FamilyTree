from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import MemberForm
from .models import Member


class AllMembers(ListView):
    template_name = "all_members.html"
    context_object_name = "all_members"

    def get_queryset(self):
        return Member.objects.all()


class Details(DetailView):
    model = Member
    template_name = "details.html"


class AddNew(CreateView):
    form_class = MemberForm
    template_name = "add_new_member.html"
    success_url = "/members/"


class EditMember(UpdateView):
    template_name = "edit_member.html"
    model = Member
    form_class = MemberForm

    def get_success_url(self):
        return f"/members/{self.object.pk}"


class DeleteMember(DeleteView):
    model = Member
    success_url = "/members/"


def main(request):
    template = "main.html"
    return render(request, template)


class TreeView(ListView):
    model = Member
    success_url = "members/tree"
    template_name = "tree.html"
    context_object_name = "members"

    def get_queryset(self):
        # TODO: return List of TreeStructures (multiple root nodes). After that write front-end using react or vue.
        father_null = Q(father_id__isnull=True)
        mother_null = Q(mother_id__isnull=True)
        roots = Member.objects.filter(father_null & mother_null).all()
        roots_with_children = [root for root in roots if root.children.count() > 0]
        return roots_with_children


class ChooseChildView(ListView):
    model = Member
    template_name = "choose_child.html"
    context_object_name = "members"

    def get_queryset(self):
        # Exclude the current member from the list to prevent them from being selected as their own child
        parent_id = self.kwargs["parent_id"]
        return Member.objects.exclude(id=parent_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent_id = self.kwargs["parent_id"]
        parent = get_object_or_404(Member, id=parent_id)
        context["parent"] = parent
        return context


def add_child_to_parent(request, parent_id, child_id):
    parent = get_object_or_404(Member, id=parent_id)
    child = get_object_or_404(Member, id=child_id)

    # Depending on the parent's sex, assign the child as a father or mother
    if parent.sex == Member.Sex.MALE:
        child.father = parent
    elif parent.sex == Member.Sex.FEMALE:
        child.mother = parent

    child.save()

    # Redirect back to the parent details page
    return redirect("members:details", parent_id)
