import pytest
from django.core.exceptions import ValidationError
from freezegun import freeze_time

from members.models import Member
from members.tests.factories import (MemberFactory, create_and_save_man,
                                     create_and_save_member,
                                     create_and_save_woman)


def test_create_default_member(db):
    expected_data = {
        "firstname": "John",
        "lastname": "Doe",
        "family_name": "Doe",
        "sex": "m",
        "birth_date": None,
        "death_date": None,
        "father": None,
        "mother": None,
        "description": None,
    }

    member: Member = MemberFactory(firstname="John", lastname="Doe", sex="m")

    for key, value in expected_data.items():
        member_value = getattr(member, key)
        assert (
            member_value == value
        ), f"Expected {key} to be {value}, but got {member_value}"


def test_link_non_existent_father_id(db):
    member = MemberFactory(father_id=999)

    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid father: Father must exist and be male.",
    ):
        member.clean()


def test_link_non_existent_mother_id(db):
    member = MemberFactory(mother_id=999)

    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid mother: Mother must exist and be female.",
    ):
        member.clean()


def test_female_as_father(db):
    mother = create_and_save_woman()
    member = MemberFactory(father_id=mother.pk)

    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid father: Father must exist and be male.",
    ):
        member.clean()


def test_male_as_mother(db):
    father = create_and_save_man()
    father.save()
    member = MemberFactory(mother_id=father.pk)

    with pytest.raises(
        ValidationError,
        match="Non-existent or invalid mother: Mother must exist and be female.",
    ):
        member.clean()


def test_invalid_sex(db):
    member = MemberFactory(sex="x")

    with pytest.raises(
        ValidationError, match="Diversity not supported. Sex must be 'm' or 'f'"
    ):
        member.clean()


def test_member_cannot_be_own_father(db):
    member = MemberFactory()
    member.save()  # if save() not performed then id=None
    member.father_id = member.pk
    with pytest.raises(ValidationError, match="A member cannot be their own father."):
        member.save()


def test_member_cannot_be_own_mother(db):
    member = MemberFactory()
    member.save()  # if save() not performed then id=None
    member.mother_id = member.pk
    with pytest.raises(ValidationError, match="A member cannot be their own mother."):
        member.save()


@pytest.mark.parametrize(
    "sex, field",
    [
        ("m", "father_id"),
        ("f", "mother_id"),
    ],
)
def test_member_children(db, sex, field):
    parent = MemberFactory(sex=sex)
    parent.save()

    data = {field: parent.id}
    child1 = MemberFactory(**data)
    child1.save()
    child2 = MemberFactory(**data)
    child2.save()

    children = parent.children

    assert set(children) == {child1, child2}
    assert children.count() == 2


@pytest.mark.parametrize("sex", ["m", "f"])
def test_family_name_defaults_to_lastname(db, sex):
    member = MemberFactory(lastname="Smith", family_name=None, sex=sex)
    member.save()

    assert member.family_name == "Smith"


def test_member_father(db):
    father = create_and_save_man(firstname="John", lastname="Doe")
    child = MemberFactory(father_id=father.pk)
    child.save()

    assert child.father == father
    assert child.father.firstname == "John"
    assert child.father.lastname == "Doe"
    assert father.children.count() == 1


def test_member_mother(db):
    mother = create_and_save_woman(firstname="Jane", lastname="Smith")
    child = MemberFactory(mother_id=mother.pk)
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
def test_save_dates_in_non_default_format(db, birth_date, death_date):
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
        # 1. Full dates ("%Y-%m-%d")
        ("2000-06-15", "2000-06-15", 0),
        ("2000-06-15", "2001-06-15", 1),
        ("2000-06-15", "2001-06-14", 0),
        ("2000-06-15", "2010-06-16", 10),
        ("2000-06-15", "2010-06-14", 9),
        # 2. Only years ("%Y") and full dates ("%Y-%m-%d")
        ("2000", "2010-06-15", 10),
        ("2000", "2009-12-31", 9),
        ("2000", "2024-06-15", 24),
        # 3. Year and month ("%Y-%m") and full dates ("%Y-%m-%d")
        ("2000-05", "2010-05-20", 10),
        ("2000-05", "2009-04-30", 8),
        # 4. Different formats for `birth_date` and `death_date` (year and month, only year)
        ("2000", "2010-05", 10),
        ("2000-06", "2010", 9),
        ("2000-06", "2010-06", 10),
        ("2000", "2000-12", 0),
        # 5. No `death_date` (so current date is set to "2024-06-15")
        ("2000-06-15", None, 24),
        ("2000", None, 24),
        ("2000-06", None, 24),
        # 6. Border days(?)
        ("2000-02-29", "2001-03-01", 1),
        ("2000-12-31", "2011-01-01", 10),
    ],
)
def test_age_property(db, birth_date, death_date, expected_age_in_years):
    member = MemberFactory(birth_date=birth_date, death_date=death_date)
    member.save()

    assert member.age == expected_age_in_years


def test_grandmother_born_before_child(db):
    grandmother = create_and_save_woman(birth_date="2020")
    father = create_and_save_man(birth_date=None, mother_id=grandmother.pk)

    child = MemberFactory(father_id=father.pk, birth_date="1990")

    with pytest.raises(
        ValidationError,
        match=f"{child.__repr__()} cannot be older than it's ancestor {grandmother.__repr__()}!",
    ):
        child.save()


def test_grandchildren_died_before_ancestor_was_born(db):
    grandx2father = create_and_save_man(birth_date="1850", death_date=None)
    grandfather = create_and_save_man(
        birth_date=None, death_date=None, father_id=grandx2father.pk
    )
    mother = create_and_save_woman(
        birth_date=None, death_date=None, father_id=grandfather.pk
    )

    child = MemberFactory(birth_date=None, death_date="1840", mother_id=mother.pk)

    with pytest.raises(
        ValidationError,
        match=f"{child.__repr__()} cannot be older than it's ancestor {grandx2father.__repr__()}!",
    ):
        child.save()


def test_circular_connections(db):
    grandx3father = create_and_save_man()
    grandx2father = create_and_save_man(father_id=grandx3father.pk)
    grandfather = create_and_save_man(father_id=grandx2father.pk)
    father = create_and_save_man(father_id=grandfather.pk)
    child = create_and_save_man(father_id=father.pk)

    with pytest.raises(
        ValidationError,
        match=f"Error: {grandx3father} and {child} are circullary connected!",
    ):
        grandx3father.father_id = child.father.pk
        grandx3father.save()


def test_siblings(db):
    parent = create_and_save_man(firstname="John")
    daughter = create_and_save_woman(father_id=parent.pk, firstname="Joanna")
    son = create_and_save_man(father_id=parent.pk, firstname="Janek")
    unrelated = create_and_save_member()

    assert list(parent.siblings) == []
    assert list(son.siblings) == [daughter]
    assert list(daughter.siblings) == [son]
    assert list(unrelated.siblings) == []


def test_siblings_property_no_parent_set(db):
    member1 = create_and_save_member()
    member2 = create_and_save_member()

    assert list(member1.siblings) == []
    assert list(member2.siblings) == []


def test_marry_divorce_then_marry_again(db):
    husband = create_and_save_man(firstname="Joe", lastname="Doe")
    wife = create_and_save_woman(firstname="Jane", lastname="Doe")

    husband.marry(wife)
    assert list(husband.spouses) == [wife]
    assert (
        list(husband.spouses[0].married) is True
    ), f"{husband} should be married with {wife}"
    assert list(wife.spouses) == [husband]
    assert (
        list(wife.spouses[0].married) is True
    ), f"{wife} should be married with {husband}"

    second_wife = create_and_save_woman(firstname="Alicia", lastname="Wonder")
    with pytest.raises(ValidationError):  # member is already! married
        husband.marry(second_wife)

    husband.divorce()
    husband.marry(second_wife)

    assert list(husband.spouses) == [wife, second_wife]
    assert (
        list(husband.spouses[0].married) is False
    ), f"{husband} should be divorced with {wife}"
    assert (
        list(husband.spouses[1].married) is True
    ), f"{husband} should be married with {second_wife}"
    assert list(wife.spouses[0].married) is False, f"{husband} divorced {wife}"
    assert list(second_wife.spouses) == [husband]
    assert (
        list(second_wife.spouses[0].married) is True
    ), f"{second_wife} should be {husband} second wife"


def test_cant_divorce_when_is_not_married(db):
    man = create_and_save_man()
    woman = create_and_save_woman()

    with pytest.raises(
        ValidationError, match=f"{man} can't divorce because he is single!"
    ):
        man.divorce()

    with pytest.raises(
        ValidationError, match=f"{woman} can't divorce because she is single!"
    ):
        woman.divorce()


"""
Features TODO:
- tree based structure

WITH RECURSIVE rectree AS (
  SELECT * 
    FROM tree 
   WHERE node_id = 1 
UNION ALL 
  SELECT t.* 
    FROM tree t 
    JOIN rectree
      ON t.parent_id = rectree.node_id
) SELECT * FROM rectree;
4.1. Retrieving Using Recursive Common Table Expressions: https://www.baeldung.com/sql/storing-tree-in-rdb
or use Dedicated Graph Database

- improved front-end (not only list based, but view tree based)
- CRUD and linking by performing UI operations, not solely based on buttons.

Future
- authorization.
- view other user family.
- add user to family and merge families.
- possibility to add one photo for each familly member.
- consider read-model in elasticsearch.
"""
