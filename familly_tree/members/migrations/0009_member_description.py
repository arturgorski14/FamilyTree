# Generated by Django 5.1.2 on 2024-11-04 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0008_alter_member_birth_date_alter_member_death_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="description",
            field=models.TextField(blank=True, max_length=2000, null=True),
        ),
    ]