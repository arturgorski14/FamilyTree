from unittest.mock import Mock

import pytest
from datetime import date
from django.core.exceptions import ValidationError
# from members.models import SpouseRelationship
from members.tests.factories import create_and_save_man, create_and_save_woman

SpouseRelationship = Mock()


@pytest.mark.django_db
class TestSpouseRelationship:

    def test_create_spouse_relationship(self):
        """Test creating a valid spouse relationship."""
        man = create_and_save_man(firstname="John", lastname="Doe")
        woman = create_and_save_woman(firstname="Jane", lastname="Doe")

        relationship = SpouseRelationship.objects.create(
            member=man,
            spouse=woman,
            marriage_date="2020-06-15"
        )

        assert relationship.member == man
        assert relationship.spouse == woman
        assert relationship.marriage_date == date(2020, 6, 15)

    def test_prevent_self_marriage(self):
        """Ensure a member cannot marry themselves."""
        man = create_and_save_man(firstname="John", lastname="Doe")

        with pytest.raises(ValidationError, match="A member cannot be married to themselves."):
            SpouseRelationship.objects.create(
                member=man,
                spouse=man,
                marriage_date="2020-06-15"
            )

    def test_prevent_double_marriage(self):
        """Ensure a member cannot be married to two people simultaneously."""
        man = create_and_save_man(firstname="John", lastname="Doe")
        woman1 = create_and_save_woman(firstname="Jane", lastname="Smith")
        woman2 = create_and_save_woman(firstname="Alice", lastname="Johnson")

        # First marriage
        SpouseRelationship.objects.create(
            member=man,
            spouse=woman1,
            marriage_date="2020-06-15"
        )

        # Attempting a second marriage
        with pytest.raises(ValidationError, match="This member already has a spouse."):
            SpouseRelationship.objects.create(
                member=man,
                spouse=woman2,
                marriage_date="2022-01-01"
            )

    def test_prevent_spouse_double_marriage(self):
        """Ensure a spouse cannot be married to multiple people."""
        man1 = create_and_save_man(firstname="John", lastname="Doe")
        man2 = create_and_save_man(firstname="Mike", lastname="Smith")
        woman = create_and_save_woman(firstname="Jane", lastname="Doe")

        # First marriage
        SpouseRelationship.objects.create(
            member=man1,
            spouse=woman,
            marriage_date="2020-06-15"
        )

        # Attempting to marry the same woman to another man
        with pytest.raises(ValidationError, match="This spouse is already married."):
            SpouseRelationship.objects.create(
                member=man2,
                spouse=woman,
                marriage_date="2022-01-01"
            )

    def test_spouse_accessor(self):
        """Test the spouse accessor property."""
        man = create_and_save_man(firstname="John", lastname="Doe")
        woman = create_and_save_woman(firstname="Jane", lastname="Doe")

        relationship = SpouseRelationship.objects.create(
            member=man,
            spouse=woman,
            marriage_date="2020-06-15"
        )

        assert man.spouse_relationship.spouse == woman
        assert woman.spouse_of == relationship
