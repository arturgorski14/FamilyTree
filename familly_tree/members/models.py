from django.core.exceptions import ValidationError
from django.db import models


class Member(models.Model):
    class Sex(models.TextChoices):
        MALE = "m"
        FEMALE = "f"

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    family_lastname = models.CharField(
        max_length=255, blank=True
    )  # TODO: change to family_name, fix default value
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MALE)
    birth_date = models.DateField(null=True, blank=True)
    is_alive = models.BooleanField(default=True)
    death_date = models.DateField(null=True, default=None, blank=True)
    father_id = models.IntegerField(null=True, blank=True)
    mother_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        born = f"born {self.birth_date}" if self.birth_date else ""
        died = (
            f"died {self.death_date}"
            if self.death_date
            else ""  # noqa E501
        )
        return f"{self.firstname} {self.lastname} {born} {died}"

    def clean(self):
        super().clean()
        self._validate_sex()
        self._validate_if_birthdate_is_before_death_date()
        self._validate_father_and_mother()

    def save(self, *args, **kwargs):
        self.clean()
        if not self.family_lastname:
            self.family_lastname = self.lastname
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

    def _validate_sex(self):
        if self.sex not in (self.Sex.MALE, self.Sex.FEMALE):
            raise ValidationError("Diversity not supported. Sex must be 'm' or 'f'")

    def _validate_if_birthdate_is_before_death_date(self):
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
