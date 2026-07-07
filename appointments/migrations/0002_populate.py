from django.db import migrations


def populate(apps, schema_editor):
    Service = apps.get_model("appointments", "Service")
    Service.objects.create(
        name="Haircut",
        description="Basic haircut service",
        price=50.00,
        duration_minutes=60,
    )
    Service.objects.create(
        name="Hair Coloring",
        description="Complete hair coloring",
        price=75.00,
        duration_minutes=120,
    )
    Service.objects.create(
        name="Shampoo and Style",
        description="Shampoo and styling service",
        price=35.00,
        duration_minutes=30,
    )

    Hairdresser = apps.get_model("appointments", "Hairdresser")
    Hairdresser.objects.create(
        first_name="Hairdresser",
        last_name="One",
        email="hairdresser.one@example.com",
    )
    Hairdresser.objects.create(
        first_name="Hairdresser",
        last_name="Two",
        email="hairdresser.two@example.com",
    )


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate),
    ]
