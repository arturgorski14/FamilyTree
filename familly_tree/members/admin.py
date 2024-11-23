from django.contrib import admin

from .models import MartialRelationship, Member


# Register your models here.
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "firstname",
        "lastname",
        "sex",
        "birth_date",
    )


class MartialRelationshipAdmin(admin.ModelAdmin):
    pass


admin.site.register(Member, MemberAdmin)
admin.site.register(MartialRelationship, MartialRelationshipAdmin)
