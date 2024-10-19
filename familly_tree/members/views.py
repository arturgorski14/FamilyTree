from django.http import HttpResponse
from django.template import loader

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
        "children_num": member.children_num,
        "birth_date": member.birth_date,
    }
    return HttpResponse(template.render(context, request))


def main(request):
    template = loader.get_template("main.html")
    return HttpResponse(template.render())


def testing(request):
    template = loader.get_template("template.html")
    context = {
        "fruits": ["Apple", "Banana", "Cherry"],
    }
    return HttpResponse(template.render(context, request))
