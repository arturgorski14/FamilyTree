from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from members.filters import MemberFilter
from members.models import Member
from members.tests.factories import (create_and_save_man,
                                     create_and_save_member,
                                     create_and_save_woman)


@pytest.mark.django_db
@freeze_time("2024-11-21")
class TestMemberFilter:
    @pytest.fixture
    def sample_data(self):
        member1 = create_and_save_man(
            firstname="John",
            lastname="Doe",
            family_name="Smith",
            birth_date=datetime.now().date() - timedelta(days=365 * 30),
            death_date=None,
        )
        member2 = create_and_save_woman(
            firstname="Jane",
            lastname="Doe",
            family_name="Smith",
            birth_date=datetime.now().date() - timedelta(days=365 * 50),
            death_date=datetime.now().date() - timedelta(days=365 * 2),
        )
        member3 = create_and_save_woman(
            firstname="Alice",
            lastname="Johnson",
            family_name="Taylor",
            birth_date=datetime.now().date() - timedelta(days=365 * 20),
            death_date=None,
        )
        member1.children_father.add(member3)
        return [member1, member2, member3]

    def test_filter_name(self, sample_data):
        filter = MemberFilter({"name": "Doe"}, queryset=Member.objects.all())
        filtered = filter.qs.order_by("id")
        assert list(filtered) == [sample_data[0], sample_data[1]]

    def test_filter_alive(self, sample_data):
        filter_alive = MemberFilter({"alive": "true"}, queryset=Member.objects.all())
        filtered_alive = filter_alive.qs.order_by("id")
        assert list(filtered_alive) == [sample_data[0], sample_data[2]]

        filter_dead = MemberFilter({"alive": "false"}, queryset=Member.objects.all())
        filtered_dead = filter_dead.qs.order_by("id")
        assert list(filtered_dead) == [sample_data[1]]

    def test_filter_sex(self, sample_data):
        filter_male = MemberFilter({"sex": "m"}, queryset=Member.objects.all())
        filtered_male = filter_male.qs.order_by("id")
        assert list(filtered_male) == [sample_data[0]]

        filter_female = MemberFilter({"sex": "f"}, queryset=Member.objects.all())
        filtered_female = filter_female.qs.order_by("id")
        assert list(filtered_female) == [sample_data[1], sample_data[2]]

    def test_filter_children_count_range(self, sample_data):
        filter_min = MemberFilter(
            {"children_count_range_min": 1}, queryset=Member.objects.all()
        )
        filtered_min = filter_min.qs.order_by("id")
        assert list(filtered_min) == [sample_data[0]]

        filter_max = MemberFilter(
            {"children_count_range_max": 0}, queryset=Member.objects.all()
        )
        filtered_max = filter_max.qs.order_by("id")
        assert list(filtered_max) == [sample_data[1], sample_data[2]]

    def test_filter_age_min(self, sample_data):
        filter_min_age = MemberFilter({"age_min": 30}, queryset=Member.objects.all())
        filtered_min_age = filter_min_age.qs.order_by("id")
        assert list(filtered_min_age) == [sample_data[0], sample_data[1]]

    def test_filter_age_max(self, sample_data):
        filter_max_age = MemberFilter({"age_max": 30}, queryset=Member.objects.all())
        filtered_max_age = filter_max_age.qs.order_by("id")
        assert list(filtered_max_age) == [sample_data[0], sample_data[2]]
