from datetime import datetime

import django_filters
from django.db.models import Count, Q

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

    children_count_range = django_filters.RangeFilter(
        method="filter_children_count_range", label="Number of Children Range"
    )

    def filter_children_count_range(self, queryset, name, value):
        # Annotate queryset to count total children from both father and mother
        queryset = queryset.annotate(
            num_children=Count("children_father") + Count("children_mother")
        )
        if value:
            min_value, max_value = value.start, value.stop
            if min_value is not None:
                queryset = queryset.filter(num_children__gte=min_value)
            if max_value is not None:
                queryset = queryset.filter(num_children__lte=max_value)

        return queryset

    # TODO: use age property from member to calculate age
    age_min = django_filters.NumberFilter(method="filter_age_min", label="Minimum Age")
    age_max = django_filters.NumberFilter(method="filter_age_max", label="Maximum Age")

    class Meta:
        model = Member
        fields = ["name", "sex", "alive", "children_count_range"]

    def filter_name(self, queryset, name, value):
        cleaned_value = value.title()
        returned_data = queryset.filter(
            Q(firstname__icontains=cleaned_value)
            | Q(lastname__icontains=cleaned_value)
            | Q(family_name__icontains=cleaned_value)
        )
        return returned_data

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
            birth_date__isnull=False, birth_date__lte=str(current_date.year - value)
        )

    def filter_age_max(self, queryset, name, value):  # TODO: fix for dead members
        # Filter by maximum age
        current_date = datetime.now().date()
        return queryset.filter(
            birth_date__isnull=False, birth_date__gte=str(current_date.year - value)
        )
