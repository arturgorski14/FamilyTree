# Generated by Django 5.1.2 on 2024-10-19 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="birth_date",
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name="member",
            name="children_num",
            field=models.IntegerField(null=True),
        ),
    ]
