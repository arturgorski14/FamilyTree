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


"""
Test cases TODO:
ultimately shouldn't be possible:
- link father_id/mother_id that doesn't exist
- link female member as father_id and vice versa
- negative children_num
- different sex than m/f
- birth_date after death_date
- is_alive=True and has death_date

ultimately should be possible:
- birth_date/death_date as not full date ie yyyy-mm-dd is a full date, so yyyy-mm and yyyy should also be valid
"""

"""
Features TODO:
- linking children
- linking valid father_id/mother_id, should append children for chosen id
- linking a child should result in adding father/mother to chosen child

2.0
- improved front-end (not only list based, but view tree based)
- CRUD and linking by performing UI operations, not solely based on buttons.

Future
- authorization.
- view other user family.
- add user to family and merge families.
- possibility to add one photo for each familly member.
- consider read-model in elasticsearch.
"""