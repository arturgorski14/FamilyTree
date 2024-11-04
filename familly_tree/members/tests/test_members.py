import factory
import pytest
from django.core.exceptions import ValidationError
from freezegun import freeze_time

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
    description = None


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
        "description": None,
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


@pytest.mark.parametrize("sex", ["m", "f"])
def test_family_name_defaults_to_lastname(db, sex):
    member = MemberFactory(lastname="Smith", family_name=None, sex=sex)
    member.save()

    assert member.family_name == "Smith"


@pytest.mark.parametrize("sex", ["m", "f"])
def test_family_name_explicitly_set(db, sex):
    member = MemberFactory(lastname="Smith", family_name="Johnson", sex=sex)
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
    "birth_date, death_date",
    [
        ("1990-05-15", "2000-01-01"),
        ("1990-05", "2024-08"),
        ("1990", "2024"),
    ],
)
def test_parse_full_date(db, birth_date, death_date):
    member = MemberFactory(birth_date=birth_date, death_date=death_date)
    member.save()

    assert member.birth_date == birth_date
    assert member.death_date == death_date


@pytest.mark.parametrize(
    "invalid_date",
    [
        "invalid-date",
        "20120-01-07",
        "2012-13-07",
        "2012-010-07",
        "2012-01-32",
        "2012-01-072",
    ],
)
@pytest.mark.parametrize("date_type", ["birth_date", "death_date"])
def test_invalid_birth_date_format(db, invalid_date, date_type):
    data = {date_type: invalid_date}
    member = MemberFactory(**data)

    with pytest.raises(
        ValidationError,
        match=f"{date_type} must be in YYYY, YYYY-MM, or YYYY-MM-DD format.",
    ):
        member.clean()


@freeze_time("2024-06-15")
def test_birth_date_before_today(db):
    member = MemberFactory(birth_date="2024-06-16")

    with pytest.raises(ValidationError, match="Birth date must be before today."):
        member.clean()


@pytest.mark.parametrize("birth_date", ["2024-05-10", "2024-05", "2024"])
@pytest.mark.parametrize("death_date", ["1999-11-28", "1999-11", "1999"])
def test_birth_date_before_death_date(db, birth_date, death_date):
    member = MemberFactory(birth_date=birth_date, death_date=death_date)
    with pytest.raises(ValidationError, match="Birth date must be before death date"):
        member.clean()


@freeze_time("2024-06-15")
@pytest.mark.parametrize(
    "birth_date, death_date, expected_age_in_years",
    [
        # 1. Kompletne daty ("%Y-%m-%d")
        ("2000-06-15", "2000-06-15", 0),
        ("2000-06-15", "2001-06-15", 1),
        ("2000-06-15", "2001-06-14", 0),
        ("2000-06-15", "2010-06-16", 10),
        ("2000-06-15", "2010-06-14", 9),
        # 2. Same lata ("%Y") i pełna data ("%Y-%m-%d")
        ("2000", "2010-06-15", 10),
        ("2000", "2009-12-31", 9),
        ("2000", "2024-06-15", 24),
        # 3. Rok i miesiąc ("%Y-%m") oraz pełna data ("%Y-%m-%d")
        ("2000-05", "2010-05-20", 10),
        ("2000-05", "2009-04-30", 8),
        # 4. Różne formaty dla `birth_date` i `death_date` (rok i miesiąc, sam rok)
        ("2000", "2010-05", 10),
        ("2000-06", "2010", 9),
        ("2000-06", "2010-06", 10),
        ("2000", "2000-12", 0),
        # 5. Brak `death_date` (czyli bieżąca data ustawiona na "2024-06-15")
        ("2000-06-15", None, 24),
        ("2000", None, 24),
        ("2000-06", None, 24),
        # 6. Dni graniczne
        ("2000-02-29", "2001-03-01", 1),
        ("2000-12-31", "2011-01-01", 10),
    ],
)
def test_age_property(db, birth_date, death_date, expected_age_in_years):
    member = MemberFactory(birth_date=birth_date, death_date=death_date)
    member.save()

    assert member.age == expected_age_in_years


"""
Features TODO:
2
- improved front-end (not only list based, but view tree based)
- CRUD and linking by performing UI operations, not solely based on buttons.

Future
- authorization.
- view other user family.
- add user to family and merge families.
- possibility to add one photo for each familly member.
- consider read-model in elasticsearch.
"""
