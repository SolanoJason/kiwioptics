# Generated by Django 3.1.6 on 2021-04-19 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medidas', '0015_auto_20210415_0516'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='is_dip',
            field=models.BooleanField(default=True, verbose_name='Dip o Dnp'),
        ),
    ]
