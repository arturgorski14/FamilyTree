from django import forms

from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member

        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Restrict the father field to male members only
        self.fields["father"].queryset = Member.objects.filter(sex=Member.Sex.MALE)

        # Restrict the mother field to female members only
        self.fields["mother"].queryset = Member.objects.filter(sex=Member.Sex.FEMALE)
