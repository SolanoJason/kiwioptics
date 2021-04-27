# Generated by Django 3.1.6 on 2021-04-15 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medidas', '0013_subsidiary_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subsidiary',
            name='direction',
            field=models.CharField(blank=True, max_length=50, verbose_name='Dirección'),
        ),
        migrations.AlterField(
            model_name='subsidiary',
            name='phone',
            field=models.CharField(blank=True, max_length=30, verbose_name='Telefono'),
        ),
        migrations.AlterField(
            model_name='subsidiary',
            name='subsidiary_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='Nombre Sucursal'),
        ),
    ]