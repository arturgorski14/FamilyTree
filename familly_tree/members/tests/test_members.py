import factory
import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase  # noqa E501

from members.forms import MemberForm
from members.models import Member


class MemberFactory(factory.Factory):
    class Meta:
        model = Member

    firstname = "John"
    lastname = "Doe"
    family_lastname = "Doe"
    sex = "m"
    birth_date = None
    is_alive = True
    death_date = None
    children_num = 0
    father_id = None
    mother_id = None


def test_create_default_member(db):
    expected_data = {
        "firstname": "John",
        "lastname": "Doe",
        "family_lastname": "Doe",
        "sex": "m",
        "birth_date": None,
        "is_alive": True,
        "death_date": None,
        "children_num": 0,
        "father_id": None,
        "mother_id": None,
    }

    member: Member = MemberFactory()

    for key, value in expected_data.items():
        member_value = getattr(member, key)
        assert (
            member_value == value
        ), f"Expected {key} to be {value}, but got {member_value}"


def test_set_family_lastname_as_lastname(db):
    """If family lastname haven't been passed, set it to member lastname"""


def test_link_non_existent_father_id(db):
    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid father: Father must exist and be male.",
    ):
        member = MemberFactory.build(father_id=999)
        member.clean()


def test_link_non_existent_mother_id(db):
    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid mother: Mother must exist and be female.",
    ):
        member = MemberFactory.build(mother_id=999)
        member.clean()


def test_female_as_father(db):
    mother: Member = MemberFactory.build(sex="f")
    mother.save()
    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid father: Father must exist and be male.",
    ):
        member = MemberFactory.build(father_id=mother.id)
        member.clean()


def test_male_as_mother(db):
    father: Member = MemberFactory.build(sex="m")
    father.save()
    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid mother: Mother must exist and be female.",
    ):
        member = MemberFactory.build(mother_id=father.id)
        member.clean()


def test_negative_children_num(db):
    with pytest.raises(ValidationError, match="Children number cannot be negative"):
        member = MemberFactory.build(children_num=-1)
        member.clean()


def test_invalid_sex(db):
    with pytest.raises(
        ValidationError, match="Diversity not supported. Sex must be 'm' or 'f'"
    ):
        member = MemberFactory.build(sex="x")
        member.clean()


def test_birth_after_death(db):
    with pytest.raises(ValidationError, match="Birth date must be before death date"):
        member = MemberFactory.build(
            birth_date="2000-01-01", is_alive=False, death_date="1999-01-01"
        )
        member.clean()


def test_is_alive_with_death_date(db):
    with pytest.raises(
        ValidationError, match="Living members cannot have a death date"
    ):
        member = MemberFactory.build(is_alive=True, death_date="2000-01-01")
        member.clean()


def test_member_cannot_be_own_father(db):
    member = MemberFactory()
    member.save()
    data = {
        "firstname": member.firstname,
        "lastname": member.lastname,
        "family_lastname": member.family_lastname,
        "father_id": member.id,
        "mother_id": member.mother_id,
        "sex": member.sex,
        "birth_date": member.birth_date,
        "is_alive": member.is_alive,
        "children_num": member.children_num,
    }

    form = MemberForm(data, instance=member)

    assert not form.is_valid()
    assert "A member cannot be their own father." in form.errors["__all__"][0]


def test_member_cannot_be_own_mother(db):
    member = MemberFactory()
    member.save()
    data = {
        "firstname": member.firstname,
        "lastname": member.lastname,
        "family_lastname": member.family_lastname,
        "father_id": member.father_id,
        "mother_id": member.id,
        "sex": member.sex,
        "birth_date": member.birth_date,
        "is_alive": member.is_alive,
        "children_num": member.children_num,
    }

    form = MemberForm(data, instance=member)

    assert not form.is_valid()
    assert "A member cannot be their own mother" in form.errors["__all__"][0]


"""
Test cases TODO:
ultimately shouldn't be possible:
- link father_id/mother_id that doesn't exist
- link female member as father_id and vice versa
- negative children_num
- different sex than m/f
- birth_date after death_date
- is_alive=True and has death_date
- set itself as father_id or mother_id

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
