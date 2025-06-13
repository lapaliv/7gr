import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Sector",
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
                ("name", models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name="Device",
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
                ("type", models.CharField(max_length=20)),
                ("host", models.CharField(max_length=15)),
                ("port", models.IntegerField()),
                ("is_automatic", models.BooleanField(default=True)),
                ("current_temperature", models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)),
                ("target_temperature", models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)),
                ("current_humidity", models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)),
                ("target_humidity", models.DecimalField(null = True, default=None, max_digits = 5, decimal_places = 2)),
                ("current_fan_speed", models.CharField(null = True, max_length=10)),
                ("target_fan_speed", models.CharField(null = True, max_length=10)),
                ("current_mode", models.CharField(null = True, max_length=10)),
                ("target_mode", models.CharField(null = True, max_length=10)),
                ("power", models.CharField(null = False, max_length=3, default = 'on')),
                (
                    "sector",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="climate.sector"
                    ),
                ),
                ("error", models.TextField(null = True)),
            ],
            options={
                "unique_together": {("host", "port")},
            },
        ),
    ]
