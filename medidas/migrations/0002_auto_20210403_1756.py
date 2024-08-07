# Generated by Django 3.1.6 on 2021-04-03 22:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('medidas', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subsidiary',
            name='optic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.opticuser', verbose_name='Optica'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='crystals',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='medidas.crystal', verbose_name='Lunas'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='doctor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Doctor'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='optic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.opticuser', verbose_name='Optica'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medidas.patient', verbose_name='Paciente'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='subsidiary',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='medidas.subsidiary', verbose_name='Sucursal'),
        ),
        migrations.AddField(
            model_name='patient',
            name='optic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.opticuser', verbose_name='Optica'),
        ),
        migrations.AddField(
            model_name='crystaltreatments',
            name='optic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.opticuser', verbose_name='Optica'),
        ),
        migrations.AddField(
            model_name='crystalmaterial',
            name='optic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.opticuser', verbose_name='Optica'),
        ),
        migrations.AddField(
            model_name='crystal',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medidas.crystalmaterial', verbose_name='Material'),
        ),
        migrations.AddField(
            model_name='crystal',
            name='optic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.opticuser', verbose_name='Optica'),
        ),
        migrations.AddField(
            model_name='crystal',
            name='treatments',
            field=models.ManyToManyField(blank=True, to='medidas.CrystalTreatments', verbose_name='Tratamientos'),
        ),
        migrations.AlterUniqueTogether(
            name='prescription',
            unique_together={('optic', 'prescription_optic_id')},
        ),
        migrations.AlterUniqueTogether(
            name='patient',
            unique_together={('optic', 'dni'), ('optic', 'patient_optic_id')},
        ),
    ]
