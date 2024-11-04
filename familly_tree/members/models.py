import re
from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.db import models


class Member(models.Model):
    class Sex(models.TextChoices):
        MALE = "m"
        FEMALE = "f"

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255, blank=True)
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MALE)
    birth_date = models.CharField(null=True, default=None, blank=True, max_length=10)
    death_date = models.CharField(null=True, default=None, blank=True, max_length=10)
    father_id = models.IntegerField(null=True, blank=True)
    mother_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True, max_length=2000)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def __repr__(self):
        born = f"born {self.birth_date}" if self.birth_date else ""
        died = f"died {self.death_date}" if self.death_date else ""  # noqa E501
        return f"{self.firstname} {self.lastname} {born} {died}"

    def clean(self):
        super().clean()
        self._validate_sex()
        self._validate_dates()
        self._validate_father_and_mother()

    def save(self, *args, **kwargs):
        self.clean()
        if not self.family_name:
            self.family_name = self.lastname
        super().save(*args, **kwargs)

    @property
    def alive(self) -> str:
        return "Yes" if self.death_date is None else "No"

    @property
    def children(self) -> list["Member"]:
        return Member.objects.filter(
            models.Q(father_id=self.id) | models.Q(mother_id=self.id)
        )

    @property
    def father(self) -> "Member":
        return Member.objects.filter(id=self.father_id).first()

    @property
    def mother(self) -> "Member":
        return Member.objects.filter(id=self.mother_id).first()

    @property
    def age(self) -> str:
        """
        Calculate age based on birth_date.
        The thicky part is that the age can be (in future versions) in different formats:
        - yyyy-mm-dd
        - yyyy-mm
        - yyyy
        Should display in years most of the time
        if member.years < 2 then display in months
        if member.years < 0 and member.months < 6 display in months with days
        """
        variable = date.today()
        return variable

    def since_death(self):
        """Follows the same logic as age propery, but using death_date"""
        raise NotImplementedError

    def _validate_sex(self):
        if self.sex not in (self.Sex.MALE, self.Sex.FEMALE):
            raise ValidationError("Diversity not supported. Sex must be 'm' or 'f'")

    def _is_birthdate_before_death_date(self):
        if not self.birth_date or not self.death_date:
            return
        if self.birth_date > self.death_date:
            raise ValidationError("Birth date must be before death date")

    def _validate_father_and_mother(self):
        if not self.father_id and not self.mother_id:
            return
        if self.father_id and self.father_id == self.id:
            raise ValidationError("A member cannot be their own father.")
        if self.mother_id and self.mother_id == self.id:
            raise ValidationError("A member cannot be their own mother.")

        parent_ids = [pid for pid in (self.father_id, self.mother_id) if pid]
        parents = Member.objects.filter(id__in=parent_ids).values("id", "sex")
        parent_lookup = {parent["id"]: parent["sex"] for parent in parents}

        if self.father_id:
            if (
                self.father_id not in parent_lookup
                or parent_lookup[self.father_id] != self.Sex.MALE
            ):
                raise ValidationError(
                    "Non-existent or invalid father: Father must exist and be male."
                )

        if self.mother_id:
            if (
                self.mother_id not in parent_lookup
                or parent_lookup[self.mother_id] != self.Sex.FEMALE
            ):
                raise ValidationError(
                    "Non-existent or invalid mother: Mother must exist and be female."
                )

    def _validate_dates(self):
        self._is_birthdate_before_death_date()

        if self.birth_date:
            try:
                self._is_valid_date_format(str(self.birth_date))
            except ValueError:
                raise ValidationError(
                    "birth_date must be in YYYY, YYYY-MM, or YYYY-MM-DD format."
                    # Date must be in 'YYYY', 'YYYY-MM', or 'YYYY-MM-DD' format and represent a valid date.
                )
        if self.death_date:
            try:
                not self._is_valid_date_format(str(self.death_date))
            except ValueError:
                raise ValidationError(
                    "death_date must be in YYYY, YYYY-MM, or YYYY-MM-DD format."
                    # Date must be in 'YYYY', 'YYYY-MM', or 'YYYY-MM-DD' format and represent a valid date.
                )

    @staticmethod
    def _is_valid_date_format(_date: str):
        """Check if the date is in a valid format and represents a real date."""
        match len(_date):
            case 4:
                datetime.strptime(_date, "%Y")
            case 7:
                datetime.strptime(_date, "%Y-%m")
            case 10:
                datetime.strptime(_date, "%Y-%m-%d")
            case _:
                raise ValueError
        return True
