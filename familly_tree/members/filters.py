from datetime import datetime

import django_filters
from django.db.models import Q, Count

from .models import Member

class MemberFilter(django_filters.FilterSet):

    SEX_CHOICES = [
        (Member.Sex.MALE, "Male"),
        (Member.Sex.FEMALE, "Female"),
    ]
    ALIVE_CHOICES = [
        ("true", "Alive"),
        ("false", "Dead"),
    ]

    name = django_filters.CharFilter(method="filter_name", label="Name")
    sex = django_filters.ChoiceFilter(choices=SEX_CHOICES, label="Sex")
    alive = django_filters.ChoiceFilter(
        choices=ALIVE_CHOICES, method="filter_alive", label="Alive"
    )

    children_count_min = django_filters.NumberFilter(
        method="filter_children_count", label="Min Number of Children"
    )
    children_count_max = django_filters.NumberFilter(
        method="filter_children_count", label="Max Number of Children"
    )

    def filter_children_count(self, queryset, name, value):
        # Annotating the queryset to count the children from both relations
        queryset = queryset.annotate(
            num_children=Count("children_father") + Count("children_mother")
        )

        if name == "children_count_min":
            return queryset.filter(num_children__gte=value)
        elif name == "children_count_max":
            return queryset.filter(num_children__lte=value)

        return queryset

    # TODO: use age property from member to calculate age
    age_min = django_filters.NumberFilter(method="filter_age_min", label="Minimum Age")
    age_max = django_filters.NumberFilter(method="filter_age_max", label="Maximum Age")

    class Meta:
        model = Member
        fields = ["name", "sex", "alive", "children_count_min", "children_count_max"]

    def filter_name(self, queryset, name, value):
        return queryset.filter(
            Q(firstname__icontains=value) | Q(lastname__icontains=value) | Q(family_name__icontains=value)
        )

    def filter_alive(self, queryset, name, value):
        if value == "true":
            return queryset.filter(death_date__isnull=True)
        elif value == "false":
            return queryset.filter(death_date__isnull=False)
        return queryset  # Return unchanged for "

    def filter_age_min(self, queryset, name, value):
        # Filter by minimum age
        current_date = datetime.now().date()
        return queryset.filter(
            birth_date__isnull=False,
            birth_date__lte=str(current_date.year - value)
        )

    def filter_age_max(self, queryset, name, value):
        # Filter by maximum age
        current_date = datetime.now().date()
        return queryset.filter(
            birth_date__isnull=False,
            birth_date__gte=str(current_date.year - value)
        )
