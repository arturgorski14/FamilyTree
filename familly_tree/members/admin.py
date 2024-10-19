from django.contrib import admin

from .models import Member


# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "firstname",
        "lastname",
        "sex",
        "birth_date",
        "is_alive",
        "children_num",
    )


admin.site.register(Member, MemberAdmin)
