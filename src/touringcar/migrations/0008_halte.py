# Generated by Django 5.0.6 on 2024-09-17 15:49

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("touringcar", "0007_alter_bericht_image_url"),
    ]

    operations = [
        migrations.CreateModel(
            name="Halte",
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
                ("code", models.IntegerField(blank=True)),
                (
                    "location",
                    models.CharField(help_text="bijzonderheden", max_length=150),
                ),
                ("capacity", models.IntegerField(help_text="plaatsen")),
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
            ],
            options={
                "abstract": False,
            },
        ),
    ]