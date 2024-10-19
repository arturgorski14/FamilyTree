# Generated by Django 5.1.2 on 2024-10-19 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0002_member_birth_date_member_children_num"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="death_date",
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="member",
            name="family_lastname",
            field=models.CharField(
                default=models.CharField(max_length=255), max_length=255
            ),
        ),
        migrations.AddField(
            model_name="member",
            name="father_id",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="member",
            name="is_alive",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="member",
            name="mother_id",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="member",
            name="sex",
            field=models.CharField(
                choices=[("m", "Male"), ("f", "Female")], default="m", max_length=1
            ),
        ),
        migrations.AlterField(
            model_name="member",
            name="children_num",
            field=models.IntegerField(default=0, null=True),
        ),
    ]
