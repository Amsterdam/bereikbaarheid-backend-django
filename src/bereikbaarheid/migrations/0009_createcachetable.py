from django.core.management import call_command
from django.db import migrations


def createcachetable(apps, schema_editor):
    call_command("createcachetable")


class Migration(migrations.Migration):
    dependencies = [
        ("bereikbaarheid", "0008_alter_venstertijdweg_verkeersbord"),
    ]

    operations = [
        migrations.RunPython(createcachetable),
    ]
