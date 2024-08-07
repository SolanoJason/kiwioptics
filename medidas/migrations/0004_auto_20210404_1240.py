# Generated by Django 3.1.6 on 2021-04-04 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medidas', '0003_auto_20210403_1913'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='crystalmaterial',
            name='retracting_index',
        ),
        migrations.AddField(
            model_name='crystalmaterial',
            name='refractive_index',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=4, null=True, verbose_name='Indice de refracción'),
        ),
        migrations.AlterField(
            model_name='crystalmaterial',
            name='material_name',
            field=models.CharField(max_length=50, verbose_name='Nombre del Material'),
        ),
        migrations.AlterField(
            model_name='crystaltreatments',
            name='treatment_name',
            field=models.CharField(max_length=50, verbose_name='Nombre del tratamiento'),
        ),
    ]
