# Generated by Django 5.0 on 2023-12-21 14:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("warehouse", "0020_alter_customerprofile_options_alter_item_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="membershiporder",
            name="payment_method",
            field=models.CharField(
                choices=[("Installment", "分期付款"), ("Full", "一次性付清")],
                default="Full",
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name="InstallmentPlan",
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
                ("due_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("paid", models.BooleanField(default=False)),
                ("payment_date", models.DateField(blank=True, null=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="installments",
                        to="warehouse.membershiporder",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PaymentAttempt",
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
                ("attempted_on", models.DateTimeField(auto_now_add=True)),
                ("success", models.BooleanField()),
                ("error_message", models.TextField(blank=True, null=True)),
                (
                    "installment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attempts",
                        to="warehouse.installmentplan",
                    ),
                ),
            ],
        ),
    ]
