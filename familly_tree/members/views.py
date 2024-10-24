import logging

from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import MemberForm
from .models import Member


class AllMembers(generic.ListView):
    template_name = "all_members.html"
    context_object_name = "mymembers"

    def get_queryset(self):
        return Member.objects.all().values()


class Details(generic.DetailView):
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
