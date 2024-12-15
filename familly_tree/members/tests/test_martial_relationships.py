import pytest
from django.core.exceptions import ValidationError

from members.models import MartialRelationship, SpouseData
from members.tests.factories import (
    create_and_save_man,
    create_and_save_member,
    create_and_save_woman,
)


def test_marriage(db):
    woman = create_and_save_woman()
    man = create_and_save_man()

    MartialRelationship.marry(woman, man)

    assert woman.spouses == [SpouseData(man, True)]
    assert man.spouses == [SpouseData(woman, True)]
    assert man.current_spouse == woman
    assert woman.current_spouse == man


def test_marriage_with_yourself(db):
    member = create_and_save_member()

    with pytest.raises(ValidationError, match=f"{member} cannot marry themselves."):
        MartialRelationship.marry(member, member)
    assert member.current_spouse is None


def test_marriage_between_two_men(db):
    man1 = create_and_save_man()
    man2 = create_and_save_man()

    with pytest.raises(ValidationError, match="Same sex marriages are not allowed"):
        MartialRelationship.marry(man1, man2)
    assert man1.current_spouse is None
    assert man2.current_spouse is None


def test_marriage_between_two_woman(db):
    woman1 = create_and_save_woman()
    woman2 = create_and_save_woman()

    with pytest.raises(ValidationError, match="Same sex marriages are not allowed"):
        MartialRelationship.marry(woman1, woman2)
    assert woman1.current_spouse is None
    assert woman2.current_spouse is None


def test_divorce(db):
    man = create_and_save_man()
    woman = create_and_save_woman()

    MartialRelationship.marry(man, woman)
    MartialRelationship.divorce(woman, man)

    assert woman.spouses == [SpouseData(man, False)]
    assert man.spouses == [SpouseData(woman, False)]
    assert woman.current_spouse is None
    assert man.current_spouse is None


def test_divorce_when_not_married(db):
    woman = create_and_save_woman(firstname="Angelina")
    man = create_and_save_man(firstname="John")
    wife = create_and_save_woman()

    MartialRelationship.marry(man, wife)

    with pytest.raises(
        ValidationError,
        match=f"{man} cannot divorce with {woman} because the are not married",
    ):
        MartialRelationship.divorce(man, woman)

    with pytest.raises(
        ValidationError,
        match=f"{woman} cannot divorce with {man} because the are not married",
    ):
        MartialRelationship.divorce(woman, man)

    assert wife.current_spouse == man
    assert man.current_spouse == wife
    assert woman.current_spouse is None


def test_second_marriage_with_the_same_person_after_divorce(db):
    man = create_and_save_man(firstname="Bob")
    woman = create_and_save_woman(firstname="Alice")
    MartialRelationship.marry(man, woman)
    MartialRelationship.divorce(man, woman)
    MartialRelationship.marry(man, woman)

    assert man.spouses == [SpouseData(woman, True)]
    assert woman.spouses == [SpouseData(man, True)]
    assert man.current_spouse == woman
    assert woman.current_spouse == man


def test_second_marriage_with_the_same_person_without_divorce(db):
    woman = create_and_save_woman(firstname="Alice")
    man = create_and_save_man(firstname="Bob")
    MartialRelationship.marry(woman, man)

    with pytest.raises(
        ValidationError, match=f"Impossible marriage because {woman} is already married"
    ):
        MartialRelationship.marry(woman, man)

    with pytest.raises(
        ValidationError, match=f"Impossible marriage because {man} is already married"
    ):
        MartialRelationship.marry(man, woman)

    assert man.spouses == [SpouseData(woman, True)]
    assert woman.spouses == [SpouseData(man, True)]
    assert man.current_spouse == woman
    assert woman.current_spouse == man


def test_second_divorce_with_the_same_person(db):
    man = create_and_save_man()
    woman = create_and_save_woman()
    MartialRelationship.marry(man, woman)
    MartialRelationship.divorce(man, woman)

    with pytest.raises(
        ValidationError,
        match=f"{man} cannot divorce with {woman} because the are not married",
    ):
        MartialRelationship.divorce(man, woman)

    with pytest.raises(
        ValidationError,
        match=f"{woman} cannot divorce with {man} because the are not married",
    ):
        MartialRelationship.divorce(woman, man)
    assert man.current_spouse is None
    assert woman.current_spouse is None


def test_married_multiple_times(db):
    husband = create_and_save_man(firstname="Joe", lastname="Doe")
    wife = create_and_save_woman(firstname="Jane", lastname="Doe")

    MartialRelationship.marry(husband, wife)
    assert husband.spouses == [
        SpouseData(wife, True)
    ], f"{husband} should be married with {wife}"
    assert wife.spouses == [
        SpouseData(husband, True)
    ], f"{wife} should be married with {husband}"

    second_wife = create_and_save_woman(firstname="Alicia", lastname="Wonder")
    with pytest.raises(
        ValidationError,
        match=f"Impossible marriage because {husband} is already married.",
    ):
        MartialRelationship.marry(husband, second_wife)

    MartialRelationship.divorce(husband, wife)
    assert husband.spouses == [
        SpouseData(wife, False)
    ], f"{husband} should be divorced with with {wife}"
    assert wife.spouses == [
        SpouseData(husband, False)
    ], f"{wife} should be divorced with with {husband}"

    MartialRelationship.marry(husband, second_wife)
    assert husband.spouses == [
        SpouseData(wife, False),
        SpouseData(second_wife, True),
    ], f"{husband} should only be married with {second_wife}"
    assert second_wife.spouses == [
        SpouseData(husband, True)
    ], f"{second_wife} should be married with {husband}"
