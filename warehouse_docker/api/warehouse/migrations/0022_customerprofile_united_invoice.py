# Generated by Django 5.0 on 2023-12-21 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0021_membershiporder_payment_method_installmentplan_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerprofile",
            name="united_invoice",
            field=models.CharField(default="0", max_length=20),
        ),
    ]
