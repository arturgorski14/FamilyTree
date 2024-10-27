import pytest
from django.contrib.auth.models import User
from django.test import TestCase  # noqa E501

from members.models import Member


def test_example():
    assert 1 == 0, "failed as expected"


def test_example_passing():
    assert 1 == 1, "passed"


def test_create_user(db):
    User.objects.create_user('test', 'test@test.com', 'pass')
    assert User.objects.count() == 1


def test_create_default_member(db):
    expected_data = dict(
        firstname="John",
        lastname="Doe",
        family_lastname="Doe",
        sex="m",
        birth_date=None,
        is_alive=True,
        death_date=None,
        children_num=0,
        father_id=None,
        mother_id=None,
    )

    member = Member(
        firstname=expected_data['firstname'],
        lastname=expected_data['lastname'],
        family_lastname=expected_data['family_lastname'],
        sex=expected_data['sex'],
        is_alive=expected_data['is_alive'],
    )

    for key, value in expected_data.items():
        member_value = getattr(member, key)
        assert member_value == value, f"value for {key=} doesn't match {member_value} != {value}"
