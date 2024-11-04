from datetime import date

import factory
import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase  # noqa E501

from members.forms import MemberForm
from members.models import Member


class MemberFactory(factory.Factory):
    class Meta:
        model = Member

    firstname = factory.Faker("first_name")
    lastname = factory.Faker("last_name")
    family_name = factory.LazyAttribute(lambda obj: obj.lastname)
    sex = factory.Iterator([Member.Sex.MALE, Member.Sex.FEMALE])
    birth_date = None
    death_date = None
    father_id = None
    mother_id = None


def test_create_default_member(db):
    expected_data = {
        "firstname": "John",
        "lastname": "Doe",
        "family_name": "Doe",
        "sex": "m",
        "birth_date": None,
        "death_date": None,
        "father_id": None,
        "mother_id": None,
    }

    member: Member = MemberFactory(firstname="John", lastname="Doe", sex="m")

    for key, value in expected_data.items():
        member_value = getattr(member, key)
        assert (
            member_value == value
        ), f"Expected {key} to be {value}, but got {member_value}"


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


def test_invalid_sex(db):
    member = MemberFactory.build(sex="x")

    with pytest.raises(
        ValidationError, match="Diversity not supported. Sex must be 'm' or 'f'"
    ):
        member.clean()


def test_member_cannot_be_own_father(db):
    member = MemberFactory()
    member.save()
    data = {
        "firstname": member.firstname,
        "lastname": member.lastname,
        "family_name": member.family_name,
        "father_id": member.id,
        "mother_id": member.mother_id,
        "sex": member.sex,
        "birth_date": member.birth_date,
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
        "family_name": member.family_name,
        "father_id": member.father_id,
        "mother_id": member.id,
        "sex": member.sex,
        "birth_date": member.birth_date,
    }

    form = MemberForm(data, instance=member)

    assert not form.is_valid()
    assert "A member cannot be their own mother" in form.errors["__all__"][0]


@pytest.mark.parametrize(
    "sex, field",
    [
        ("m", "father_id"),
        ("f", "mother_id"),
    ],
)
def test_member_children(db, sex, field):
    parent = MemberFactory.build(sex=sex)
    parent.save()

    data = {field: parent.id}
    child1 = MemberFactory.build(**data)
    child1.save()
    child2 = MemberFactory.build(**data)
    child2.save()

    children = parent.children

    assert set(children) == {child1, child2}
    assert children.count() == 2


def test_family_name_defaults_to_lastname(db):
    member = MemberFactory(lastname="Smith", family_name=None)
    member.save()

    assert member.family_name == "Smith"


def test_family_name_explicitly_set(db):
    member = MemberFactory(lastname="Smith", family_name="Johnson")
    member.save()

    assert member.family_name == "Johnson"


def test_member_father(db):
    father = MemberFactory(firstname="John", lastname="Doe", sex="m")
    father.save()
    child = MemberFactory(father_id=father.id)
    child.save()

    assert child.father == father
    assert child.father.firstname == "John"
    assert child.father.lastname == "Doe"
    assert father.children.count() == 1


def test_member_mother(db):
    mother = MemberFactory(firstname="Jane", lastname="Smith", sex="f")
    mother.save()
    child = MemberFactory(mother_id=mother.id)
    child.save()

    assert child.mother == mother
    assert child.mother.firstname == "Jane"
    assert child.mother.lastname == "Smith"
    assert mother.children.count() == 1


def test_member_father_not_set(db):
    child = MemberFactory(father_id=None)
    child.save()

    assert child.father is None


def test_member_mother_not_set(db):
    child = MemberFactory(mother_id=None)
    child.save()

    assert child.mother is None


def test_member_alive(db):
    member = MemberFactory(death_date=None)
    member.save()

    assert member.alive == "Yes"
    assert member.death_date is None


def test_member_not_alive(db):
    death_date = "2000-01-01"
    member = MemberFactory(death_date=death_date)
    member.save()

    assert member.alive == "No"
    assert member.death_date == death_date


@pytest.mark.parametrize(
    "birth_date",
    [
        "1990-05-15",
        # "1990-05",
        # "1990",
    ],
)
def test_parse_full_birth_date(db, birth_date):
    member = MemberFactory(birth_date=birth_date)
    member.save()

    assert member.birth_date == birth_date


@pytest.mark.parametrize(
    "death_date",
    [
        "2000-01-01",
        # "2024-08",
        # "2024",
    ],
)
def test_parse_full_death_date(db, death_date):
    member = MemberFactory(death_date=death_date)
    member.save()

    assert member.death_date == death_date


def test_invalid_birth_date_format(db):  # TODO: add death_date
    member = MemberFactory(birth_date="invalid-date")
    with pytest.raises(
        ValidationError,
        match="birth_date must be in YYYY, YYYY-MM, or YYYY-MM-DD format.",
    ):
        member.clean()


@pytest.mark.parametrize(
    "birth_date, death_date",
    [
        ("1990", "1980"),
    ],
)
def test_birth_date_before_death_date(db, birth_date, death_date):
    member = Member(
        firstname="John", lastname="Doe", birth_date=birth_date, death_date=death_date
    )
    with pytest.raises(ValidationError, match="Birth date must be before death date"):
        member.clean()


"""
Features TODO:
- birth_date/death_date as not full date ie yyyy-mm-dd is a full date, so yyyy-mm and yyyy should also be valid
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
