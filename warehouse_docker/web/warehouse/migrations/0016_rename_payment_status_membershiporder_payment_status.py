# Generated by Django 4.1 on 2023-12-05 14:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0015_remove_membershiporder_payment_status_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="membershiporder",
            old_name="Payment_status",
            new_name="payment_status",
        ),
    ]