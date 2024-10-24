import logging

from django.http import HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views import generic, View
from django.views.generic import CreateView, FormView

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

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            data = self._clean_data(request.POST)
            new_member = Member(
                firstname=data["firstname"],
                lastname=data["lastname"],
                family_lastname=data["family_lastname"],
                sex=data["sex"],
                birth_date=data["birth_date"],
                is_alive=data["is_alive"],
                death_date=data["death_date"],
                children_num=data["children_num"],
                father_id=data["father_id"],
                mother_id=data["mother_id"],
            )
            new_member.save()
            return HttpResponseRedirect("/members/")
        context = {"form": form}
        return render(request, self.template_name, context)

    def _clean_data(self, data: QueryDict) -> dict:  # Something like marshmallow schema would be usefull
        cleaned_data = data.copy()
        cleaned_data.pop("csrfmiddlewaretoken")
        set_is_alive = data["is_alive"] == "on" if "is_alive" in data else True
        set_birthdate = (
            data["birth_date"]
            if "birth_date" in data and data["birth_date"]
            else None  # noqa E501
        )
        set_deathdate = (
            data["death_date"]
            if "death_date" in data and data["death_date"]
            else None  # noqa E501
        )
        set_father_id = data["father_id"] if data["father_id"] else None
        set_mother_id = data["mother_id"] if data["mother_id"] else None

        cleaned_data["is_alive"] = set_is_alive
        cleaned_data["birth_date"] = set_birthdate
        cleaned_data["death_date"] = set_deathdate
        cleaned_data["father_id"] = set_father_id
        cleaned_data["mother_id"] = set_mother_id
        return cleaned_data


def edit(request, pk: int):
    member = get_object_or_404(Member, id=pk)
    form = MemberForm(instance=member)
    if request.method == "POST":
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            logging.warning("saved")
            return HttpResponseRedirect(f"/members/details/{pk}")

    template = "edit_member.html"
    context = {
        "form": form,
    }
    return render(request, template, context)


def remove(request, pk: int):
    member = get_object_or_404(Member, id=pk)
    member.delete()
    return HttpResponseRedirect("/members")


def main(request):
    template = "main.html"
    return render(request, template)
