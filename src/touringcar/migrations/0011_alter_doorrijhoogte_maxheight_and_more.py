# Generated by Django 5.0.6 on 2024-09-19 15:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("touringcar", "0010_doorrijhoogte_alter_parkeerplaats_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doorrijhoogte",
            name="maxheight",
            field=models.CharField(
                help_text="maximaleDoorrijhoogte",
                max_length=5,
                validators=[
                    django.core.validators.RegexValidator(
                        message="format voor maximaledoorijhoogte is: <cijfer>,<cijfer> gevolgd door 'm'",
                        regex="^\\d+[,]{0,1}\\d{0,}m$",
                    )
                ],
            ),
        ),
        migrations.AddConstraint(
            model_name="doorrijhoogte",
            constraint=models.UniqueConstraint(
                fields=("name", "lat", "lon"), name="doorrijhoogte_name_lat_lon_unique"
            ),
        ),
        migrations.AddConstraint(
            model_name="halte",
            constraint=models.UniqueConstraint(
                fields=("name",), name="halte_name_unique"
            ),
        ),
        migrations.AddConstraint(
            model_name="parkeerplaats",
            constraint=models.UniqueConstraint(
                fields=("name",), name="parkeerplaats_name_unique"
            ),
        ),
    ]
