# Generated by Django 4.2.7 on 2023-11-27 09:36

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("touringcar", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bericht",
            name="geometry",
            field=django.contrib.gis.db.models.fields.PointField(
                default="SRID=28992;POINT (122025.8 488234.44)", srid=28992
            ),
        ),
    ]