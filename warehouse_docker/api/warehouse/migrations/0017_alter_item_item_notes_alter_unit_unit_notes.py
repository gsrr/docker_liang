# Generated by Django 4.1 on 2023-12-12 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0016_rename_payment_status_membershiporder_payment_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="item_notes",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="unit",
            name="unit_notes",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
