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

    age_range = django_filters.RangeFilter(method="filter_age_range", label="Age Range")

    def filter_children_count_range(self, queryset, name, value):
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

    def filter_age_range(self, queryset, name, value):
        if value:
            min_value, max_value = value.start, value.stop
            if min_value is not None:
                queryset = queryset.filter(cached_age__gte=min_value)
            if max_value is not None:
                queryset = queryset.filter(cached_age__lte=max_value)

        return queryset

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
        return queryset

    def filter_age_min(self, queryset, name, value):
        return queryset.filter(cached_age__gte=value)

    def filter_age_max(self, queryset, name, value):
        return queryset.filter(cached_age__lte=value)
