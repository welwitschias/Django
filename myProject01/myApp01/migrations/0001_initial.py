# Generated by Django 4.1.2 on 2022-10-24 01:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Board",
            fields=[
                ("idx", models.AutoField(primary_key=True, serialize=False)),
                ("writer", models.CharField(max_length=50)),
                ("title", models.CharField(max_length=200)),
                ("content", models.TextField()),
                ("hit", models.IntegerField(default=0)),
                (
                    "post_date",
                    models.DateTimeField(blank=True, default=datetime.datetime.now),
                ),
                ("filename", models.CharField(blank=True, default="", max_length=500)),
                ("filesize", models.IntegerField(default=0)),
                ("down", models.IntegerField(default=0)),
            ],
        ),
    ]
