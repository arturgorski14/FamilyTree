import logging
from datetime import timezone

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.views.generic.detail import DetailView

from .forms import MemberForm
from .models import Member


def members(request):
    template = loader.get_template("all_members.html")
    all_members = Member.objects.all().values()
    context = {"mymembers": all_members}
    return HttpResponse(template.render(context, request))


def details(request, pk: int):
    member = Member.objects.get(id=pk)
    template = loader.get_template("details.html")
    context = {
        "firstname": member.firstname,
        "lastname": member.lastname,
        "family_lastname": member.family_lastname,
        "sex": member.sex,
        "birth_date": member.birth_date,
        "is_alive": member.is_alive,
        "death_date": member.death_date,
        "children_num": member.children_num,
        "father_id": member.father_id,
        "mother_id": member.mother_id,
    }
    return HttpResponse(template.render(context, request))


def add_new(request):
    if request.POST:
        data: MemberForm = request.POST
        set_is_alive = data["is_alive"] == "on" if "is_alive" in data else True
        set_birthdate = (
            data["birth_date"] if "birth_date" in data and data["birth_date"] else None
        )
        set_deathdate = (
            data["death_date"] if "death_date" in data and data["death_date"] else None
        )
        new_member = Member(
            firstname=data["firstname"],
            lastname=data["lastname"],
            family_lastname=data["family_lastname"],
            sex=data["sex"],
            birth_date=set_birthdate,
            is_alive=set_is_alive,
            death_date=set_deathdate,
            children_num=data["children_num"],
        )
        new_member.save()
        return HttpResponseRedirect("/members")
    template = loader.get_template("add_new_member.html")
    form = MemberForm()
    context = {"error_message": "You didn't select a choice.", "form": form}
    return HttpResponse(template.render(context, request))


def edit(request, pk: int):
    member = Member.objects.get(id=pk)
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
    member = Member.objects.get(id=pk)
    member.delete()
    return HttpResponseRedirect(f"/members")


def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())
