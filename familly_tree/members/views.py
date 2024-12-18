from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django_filters.views import FilterView

from .filters import MemberFilter
from .forms import MemberForm
from .models import MartialRelationship, Member


class AllMembers(FilterView):
    model = Member
    template_name = "all_members.html"
    context_object_name = "all_members"
    filterset_class = MemberFilter

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
        parent_id = self.kwargs["parent_id"]
        parent = get_object_or_404(Member, id=parent_id)

        # Filter out the parent (itself) and members born before itself
        queryset = Member.objects.exclude(id=parent_id)

        if parent.birth_date:
            queryset = queryset.filter(
                Q(birth_date__isnull=True) | Q(birth_date__gt=parent.birth_date)
            )
        else:
            queryset = queryset

        return queryset

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


class MemberMarriagesView(ListView):
    model = MartialRelationship
    template_name = "member_marriages.html"
    context_object_name = "marriages"

    def get_queryset(self):
        member_id = self.kwargs["member_id"]
        return MartialRelationship.objects.filter(member_id=member_id).select_related(
            "spouse"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = get_object_or_404(Member, pk=self.kwargs["member_id"])
        return context


class MarryMemberCreateView(CreateView):
    model = MartialRelationship
    fields = ["spouse"]
    template_name = "marry_member_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_id"] = self.kwargs["member_id"]
        return context

    def form_valid(self, form):
        member = get_object_or_404(Member, pk=self.kwargs["member_id"])
        spouse = form.cleaned_data["spouse"]

        MartialRelationship.marry(member, spouse)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "members:member_marriages", kwargs={"member_id": self.kwargs["member_id"]}
        )


def marry_member(request, member_id, spouse_id):
    member = get_object_or_404(Member, pk=member_id)
    spouse = get_object_or_404(Member, pk=spouse_id)
    MartialRelationship.marry(member, spouse)
    return redirect("members:member_marriages", member_id=member_id)


def divorce_member(request, member_id, spouse_id):
    member = get_object_or_404(Member, pk=member_id)
    spouse = get_object_or_404(Member, pk=spouse_id)
    MartialRelationship.divorce(member, spouse)
    return redirect("members:member_marriages", member_id=member_id)
