from django.db import models


class Member(models.Model):
    class Sex(models.TextChoices):
        MALE = "m"
        FEMALE = "f"

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    family_lastname = models.CharField(max_length=255, default=lastname)
    sex = models.CharField(max_length=1, choices=Sex, default=Sex.MALE)
    birth_date = models.DateField(null=True)
    is_alive = models.BooleanField(default=True)
    death_date = models.DateField(
        null=True, default=None
    )  # only show's up when is_alive is False
    children_num = models.IntegerField(null=True, default=0)
    father_id = models.IntegerField(null=True)  # noone knows who was before him
    mother_id = models.IntegerField(null=True)  # noone knows who was before her
