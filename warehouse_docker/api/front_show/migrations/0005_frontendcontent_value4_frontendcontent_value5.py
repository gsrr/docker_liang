# Generated by Django 5.0 on 2024-01-15 04:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('front_show', '0004_alter_frontendcontent_value1'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontendcontent',
            name='value4',
            field=models.TextField(blank=True, null=True, verbose_name='Content4'),
        ),
        migrations.AddField(
            model_name='frontendcontent',
            name='value5',
            field=models.TextField(blank=True, null=True, verbose_name='Content5'),
        ),
    ]