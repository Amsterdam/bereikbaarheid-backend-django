# Generated by Django 5.0.6 on 2024-09-18 12:29

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("touringcar", "0009_parkeerplaats"),
    ]

    operations = [
        migrations.CreateModel(
            name="Doorrijhoogte",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(help_text="omschrijving", max_length=50)),
                ("lat", models.FloatField(blank=True, help_text="Latitude", null=True)),
                (
                    "lon",
                    models.FloatField(blank=True, help_text="Longitude", null=True),
                ),
                (
                    "geometry",
                    django.contrib.gis.db.models.fields.PointField(
                        default="SRID=28992;POINT (122025.8 488234.44)", srid=28992
                    ),
                ),
                (
                    "maxheight",
                    models.CharField(
                        help_text="maximaleDoorrijhoogte",
                        max_length=5,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid registration number in the format ABC123.",
                                regex="^\\d+,\\d+m$",
                            )
                        ],
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterModelOptions(
            name="parkeerplaats",
            options={"verbose_name_plural": "Parkeerplaatsen"},
        ),
    ]