from django.contrib import admin

from .models import Member


# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "firstname",
        "lastname",
        "sex",
        "birth_date",
    )


admin.site.register(Member, MemberAdmin)
