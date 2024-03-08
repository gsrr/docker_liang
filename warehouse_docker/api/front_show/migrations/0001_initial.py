# Generated by Django 5.0 on 2024-01-14 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FrontEndContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True, verbose_name='Key')),
                ('value', models.TextField(verbose_name='Content')),
            ],
            options={
                'verbose_name': 'Front End Content',
                'verbose_name_plural': 'Front End Contents',
            },
        ),
        migrations.CreateModel(
            name='FrontEndImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100, unique=True, verbose_name='Key')),
                ('image', models.ImageField(upload_to='page_images/', verbose_name='Image')),
            ],
            options={
                'verbose_name': 'Front End Image',
                'verbose_name_plural': 'Front End Images',
            },
        ),
    ]