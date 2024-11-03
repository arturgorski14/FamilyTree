# Generated by Django 5.1.2 on 2024-11-02 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0004_alter_member_birth_date_alter_member_children_num_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="children_num",
        ),
        migrations.AlterField(
            model_name="member",
            name="family_lastname",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]