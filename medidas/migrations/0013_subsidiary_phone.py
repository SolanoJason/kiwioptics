# Generated by Django 3.1.6 on 2021-04-15 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medidas', '0012_auto_20210414_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='subsidiary',
            name='phone',
            field=models.CharField(blank=True, max_length=30, verbose_name='Celular'),
        ),
    ]
