# Generated by Django 5.0 on 2023-12-21 16:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0022_customerprofile_united_invoice"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="installmentplan",
            name="order",
        ),
        migrations.CreateModel(
            name="Invoice",
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
                ("invoice_number", models.CharField(max_length=50)),
                ("invoice_date", models.DateField(auto_now_add=True)),
                ("is_sent", models.BooleanField(default=False)),
                (
                    "installment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="warehouse.installmentplan",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PaymentPlan",
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
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("number_of_installments", models.IntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_plans",
                        to="warehouse.membershiporder",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="installmentplan",
            name="payment_plan",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="installments",
                to="warehouse.paymentplan",
            ),
        ),
        migrations.DeleteModel(
            name="PaymentAttempt",
        ),
    ]
