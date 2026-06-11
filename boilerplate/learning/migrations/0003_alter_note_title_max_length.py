from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0002_alter_note_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="note",
            name="title",
            field=models.CharField(max_length=500),
        ),
    ]

