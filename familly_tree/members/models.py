from django.db import models


class Member(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    children_num = models.IntegerField(null=True)
    birth_date = models.DateField(null=True)

    def __repr__(self):
        return f"{self.firstname} {self.lastname} born {self.birth_date} has {self.children_num} children"
