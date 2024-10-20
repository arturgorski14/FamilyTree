from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse

from .forms import MemberForm
from .models import Member


def members(request):
    template = loader.get_template("all_members.html")
    all_members = Member.objects.all().values()
    context = {"mymembers": all_members}
    return HttpResponse(template.render(context, request))


def details(request, id):
    member = Member.objects.get(id=id)
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
        birthdate = data["birth_date"] if data["birth_date"] else None
        is_alive = True if data["is_alive"] == "on" else False
        deathdate = data["death_date"] if data["death_date"] else None
        new_member = Member(
            firstname=data["firstname"],
            lastname=data["lastname"],
            family_lastname=data["family_lastname"],
            sex=data["sex"],
            birth_date=birthdate,
            is_alive=is_alive,
            death_date=deathdate,
            children_num=data["children_num"],
        )
        new_member.save()
        return HttpResponseRedirect("/members")
    template = loader.get_template("add_new_member.html")
    form = MemberForm()
    context = {"error_message": "You didn't select a choice.", "form": form}
    return HttpResponse(template.render(context, request))


def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())
