import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from members.models import MartialRelationship
from members.tests.factories import (create_and_save_man,
                                     create_and_save_member,
                                     create_and_save_woman)


def test_marry_member_success(client, db):
    man = create_and_save_man()
    woman = create_and_save_woman()

    assert (
        MartialRelationship.objects.count() == 0
    ), f"{MartialRelationship.objects.all()}"

    url = reverse(
        "members:marry_member", kwargs={"member_id": man.pk, "spouse_id": woman.pk}
    )
    response = client.get(url)

    assert response.status_code == 302

    assert MartialRelationship.objects.filter(
        member=man, spouse=woman, married=True
    ).exists()
    assert MartialRelationship.objects.filter(
        member=woman, spouse=man, married=True
    ).exists()

    assert (
        MartialRelationship.objects.count() == 2
    ), f"{MartialRelationship.objects.all()}"


@pytest.mark.parametrize("function", [create_and_save_man, create_and_save_woman])
def test_cannot_marry_member_with_same_sex(client, db, function):
    member1 = function()
    member2 = function()

    url = reverse(
        "members:marry_member",
        kwargs={"member_id": member1.pk, "spouse_id": member2.pk},
    )

    with pytest.raises(ValidationError, match="Same sex marriages are not allowed"):
        client.get(url)


def test_cannot_marry_already_married_member(client, db):
    member_1 = create_and_save_woman()
    member_2 = create_and_save_man()
    member_3 = create_and_save_man()
    MartialRelationship.marry(member_1, member_3)

    url = reverse(
        "members:marry_member",
        kwargs={"member_id": member_1.pk, "spouse_id": member_2.pk},
    )

    with pytest.raises(
        ValidationError,
        match=f"Impossible marriage because {member_1} is already married.",
    ):
        client.get(url)


def test_cannot_marry_yourself(client, db):
    member_1 = create_and_save_member()

    url = reverse(
        "members:marry_member",
        kwargs={"member_id": member_1.pk, "spouse_id": member_1.pk},
    )

    with pytest.raises(ValidationError, match=f"{member_1} cannot marry themselves."):
        client.get(url)
