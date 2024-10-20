from django.db import models


class Member(models.Model):
    class Sex(models.TextChoices):
        MALE = "m"
        FEMALE = "f"

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    family_lastname = models.CharField(
        max_length=255, default=lastname
    )  # TODO: change to family_name, fix default value
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MALE)
    birth_date = models.DateField(null=True, blank=True)  # TODO: change to birthdate
    is_alive = models.BooleanField(default=True)
    death_date = models.DateField(
        null=True, default=None, blank=True
    )  # only show's up when is_alive is False
    children_num = models.IntegerField(default=0)
    father_id = models.IntegerField(
        null=True, blank=True
    )  # noone knows who was before him
    mother_id = models.IntegerField(
        null=True, blank=True
    )  # noone knows who was before her

    def __str__(self):
        born = f"born {self.birth_date}" if self.birth_date else ""
        died = (
            f"died {self.death_date}" if not self.is_alive and self.death_date else ""
        )
        return f"{self.firstname} {self.lastname} {born} {died}"
