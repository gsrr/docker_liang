# Generated by Django 4.1 on 2023-12-12 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0017_alter_item_item_notes_alter_unit_unit_notes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="item_notes",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
