"""Initial schema for the learning app."""

from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the Note model."""

    # First migration for the learning app.
    initial = True

    # No dependencies because this is the first migration.
    dependencies = []

    operations = [
        # Create the Note table with timestamp fields.
        migrations.CreateModel(
            name="Note",
            fields=[
                # Primary key field.
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120)),
                ("body", models.TextField(blank=True)),
                ("is_archived", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
