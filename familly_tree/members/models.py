from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch, Q, QuerySet


class Member(models.Model):
    class Sex(models.TextChoices):
        MALE = "m", "Male"
        FEMALE = "f", "Female"

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255, blank=True)
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MALE)
    birth_date = models.CharField(null=True, default=None, blank=True, max_length=10)
    death_date = models.CharField(null=True, default=None, blank=True, max_length=10)
    description = models.TextField(null=True, blank=True, max_length=2000)

    father = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children_father",
    )
    mother = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children_mother",
    )

    def __repr__(self):
        born = f" born {self.birth_date}" if self.birth_date else ""
        died = f" died {self.death_date}" if self.death_date else ""
        return f"{self.firstname} {self.lastname}{born}{died}"

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def clean(self):
        super().clean()
        self._validate_sex()
        self._validate_dates()
        self._validate_father_and_mother()
        self._validate_ancestor()

    def save(self, *args, **kwargs):
        self.clean()
        self.firstname = self.firstname.capitalize()
        self.lastname = self.lastname.capitalize()
        if not self.family_name:
            self.family_name = self.lastname
        else:
            self.family_name = self.family_name.capitalize()
        super().save(*args, **kwargs)

    @property
    def age(self) -> int:
        """
        Calculate age based on birth_date and death_date.
        The thicky part is that the age can be (in future versions) in different formats:
        - yyyy-mm-dd
        - yyyy-mm
        - yyyy
        Should display in years most of the time (but for now just full years will be enough):
        if member.years < 2 then display in months
        if member.years < 0 and member.months < 6 display in months with days
        """
        return self.__calculate_age()

    @property
    def alive(self) -> str:
        return "Yes" if self.death_date is None else "No"

    @property
    def children(self) -> QuerySet:
        if self.sex == self.Sex.MALE:
            query_filter = Q(father__isnull=False, father=self)
        else:
            query_filter = Q(mother__isnull=False, mother=self)
        return Member.objects.filter(query_filter)

    @property
    def siblings(self) -> QuerySet:
        father_filter = Q(father__isnull=False, father=self.father)
        mother_filter = Q(mother__isnull=False, mother=self.mother)
        return Member.objects.filter(father_filter | mother_filter).exclude(id=self.pk)

    @property
    def since_death(self) -> int:
        """Follows the same logic as age propery, but using death_date"""
        raise NotImplementedError

    @property
    def spouses(self) -> list["SpouseData"]:
        """Return all the spouses."""
        return MartialRelationship.spouses(self)

    @property
    def current_spouse(self) -> Optional["Member"]:
        current_spouses = [
            spouse_data.spouse for spouse_data in self.spouses if spouse_data.married
        ]
        if len(current_spouses) == 1:
            return current_spouses[0]
        elif len(current_spouses) > 1:
            raise ValueError(
                f"{self} has more than 1 current spouse! {current_spouses}"
            )
        else:
            return None

    def _validate_dates(self) -> None:
        if self.birth_date:
            try:
                self._is_valid_date_format(str(self.birth_date))
            except ValueError:
                raise ValidationError(
                    "birth_date must be in YYYY, YYYY-MM, or YYYY-MM-DD format."
                    # Date must be in 'YYYY', 'YYYY-MM', or 'YYYY-MM-DD' format and represent a valid date.
                )
            if self._is_birthday_before_today():
                raise ValidationError("Birth date must be before today.")
        if self.death_date:
            try:
                not self._is_valid_date_format(str(self.death_date))
            except ValueError:
                raise ValidationError(
                    "death_date must be in YYYY, YYYY-MM, or YYYY-MM-DD format."
                    # Date must be in 'YYYY', 'YYYY-MM', or 'YYYY-MM-DD' format and represent a valid date.
                )

        self.__is_birthdate_before_death_date()

    def _validate_father_and_mother(self) -> None:
        if self.father_id and self.father_id == self.pk:
            raise ValidationError("A member cannot be their own father.")
        if self.mother_id and self.mother_id == self.pk:
            raise ValidationError("A member cannot be their own mother.")
        if not self.father_id and not self.mother_id:
            return

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

    def _validate_sex(self) -> None:
        if self.sex not in (self.Sex.MALE, self.Sex.FEMALE):
            raise ValidationError("Diversity not supported. Sex must be 'm' or 'f'")

    def _validate_ancestor(self) -> None:
        pass

    def __is_birthdate_before_death_date(self) -> None:
        if not self.birth_date or not self.death_date:
            return
        if self.birth_date > self.death_date:
            raise ValidationError("Birth date must be before death date")

    def _is_birthday_before_today(self) -> bool:
        today = date.today()
        parsed_date = self.__parse_date(str(self.birth_date))
        if parsed_date is None:
            return False
        return today <= parsed_date

    @staticmethod
    def _is_valid_date_format(_date: str) -> str | bool:
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

    def __calculate_age(self) -> Optional[int]:
        """Calculate age based on birth_date and death_date, if provided."""
        birth_date = self.__parse_date(str(self.birth_date))
        if not birth_date:
            return None

        death_date = (
            self.__parse_date(str(self.death_date)) or datetime.now().date()
        )  # Use current date if no death_date

        # Calculate the difference in years, months, and days
        age_years = death_date.year - birth_date.year
        if death_date.month < birth_date.month or (
            death_date.month == birth_date.month and death_date.day < birth_date.day
        ):
            age_years -= 1  # Adjust if birth date hasn't occurred yet this year

        return age_years

    def __parse_date(self, date_str) -> datetime.date:
        """Parse date_str into a date object. Partial dates default to the start of the month/year."""
        if not date_str:
            return None
        try:
            if len(date_str) == 10:  # "YYYY-MM-DD"
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            elif len(date_str) == 7:  # "YYYY-MM"
                return datetime.strptime(date_str, "%Y-%m").date()
            elif len(date_str) == 4:  # "YYYY"
                return datetime.strptime(date_str, "%Y").date()
        except ValueError:
            return None


@dataclass
class SpouseData:
    spouse: Member
    married: bool


class MartialRelationship(models.Model):
    """
    Tracks current and previous marriages.
    married=True - Two members are married.
    married=False - Two members are divorced.
    """

    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="martialrelationship"
    )
    spouse = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="spouse_relationships"
    )
    married = models.BooleanField(default=True)

    @staticmethod
    def spouses(member: Member) -> list[SpouseData]:
        relationships = MartialRelationship.objects.filter(member=member)
        return [SpouseData(rel.spouse, rel.married) for rel in relationships]

    @staticmethod
    def current_spouse(member: Member) -> Member:
        spouse = MartialRelationship.objects.filter(member=member, married=True)
        return spouse

    @staticmethod
    def marry(member: Member, spouse: Member):
        """Marry a spouse."""
        if member == spouse:
            raise ValidationError(f"{member} cannot marry themselves.")
        if member.sex == spouse.sex:
            raise ValidationError("Same sex marriages are not allowed")
        if any(s.married for s in member.spouses):
            raise ValidationError(
                f"Impossible marriage because {member} is already married."
            )
        if any(s.married for s in spouse.spouses):
            raise ValidationError(
                f"Impossible marriage because {spouse} is already married."
            )
        MartialRelationship.objects.create(member=member, spouse=spouse, married=True)
        MartialRelationship.objects.create(member=spouse, spouse=member, married=True)

    @staticmethod
    def divorce(member: Member, spouse: "Member"):
        """Divorce a spouse."""
        if member.current_spouse != spouse:
            raise ValidationError(
                f"{member} cannot divorce with {spouse} because the are not married"
            )
        MartialRelationship.objects.filter(
            member=member, spouse=spouse, married=True
        ).update(married=False)
        MartialRelationship.objects.filter(
            member=spouse, spouse=member, married=True
        ).update(married=False)

    def __str__(self):
        return f"{self.member} and {self.spouse} are{' not' if not self.married else ''} married"
