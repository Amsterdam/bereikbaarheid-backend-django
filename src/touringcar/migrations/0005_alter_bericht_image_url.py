# Generated by Django 5.0.1 on 2024-01-26 12:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("touringcar", "0004_alter_bericht_image_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bericht",
            name="image_url",
            field=models.ImageField(blank=True, null=True, upload_to="images"),
        ),
    ]