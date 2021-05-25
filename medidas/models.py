from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from .custom_functions import isOnlyOneTrue
from users.models import OpticUser, Account
import decimal
from termcolor import colored

# Create your models here.


class Patient(models.Model):

    class Gender(models.TextChoices):
        MALE = 'MALE', 'Masculino'
        FEMALE = 'FEMALE', 'Femenino'
        OTHER = 'OTHER', 'Otro'

    patient_optic_id = models.PositiveIntegerField(blank=True)
    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)
    full_name = models.CharField("Nombre completo", max_length=100)
    dni = models.CharField(
        "Dni o Pasaporte", max_length=20, blank=True, null=True)
    age = models.PositiveSmallIntegerField("Edad", blank=True, null=True)
    gender = models.CharField("Genero", max_length=20,
                              blank=True, choices=Gender.choices)
    phone = models.CharField("Celular", max_length=30, blank=True)
    job = models.CharField('Ocupacion', max_length=70, blank=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        unique_together = (('optic', 'dni'), ('optic', 'patient_optic_id'))

    def __str__(self):
        return f"{self.full_name}"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self._state.adding is True:
            optic = OpticUser.objects.get(pk=self.optic.id)
            last_patient = optic.patient_set.last()
            if last_patient:
                patient_optic_id = last_patient.patient_optic_id + 1
            else:
                patient_optic_id = 1
            self.patient_optic_id = patient_optic_id
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class DiagnosisChoices(models.TextChoices):
    MYOPIA = 'MYOPIA', 'Miopía'
    ASTIGMATISM = 'ASTIGMATISM', 'Astigmatismo'
    FARSIGHTEDNESS = 'FARSIGHTEDNESS', 'Hipermetropía'
    PRESBYOPIA = 'PRESBYOPIA', 'Presbicia'
    SQUINT = 'SQUINT', 'Estrabismo'
    AMBLYOPIA = 'AMBLYOPIA', 'Ambliopía'
    DIOPIA = 'DIOPIA', 'Diopía'
    GLAUCOMA = 'GLAUCOMA', 'Glaucoma'
    DETACHED_RETINA = 'DETACHED_RETINA', 'Desprendimiento de la retina'
    CATARACT = 'CATARACT', 'Catarata'
    DALTONISM = 'DALTONISM', 'Daltonismo'
    CONJUNCTIVITIS = 'CONJUNCTIVITIS', 'Conjuntivitis'
    DIABETIC_RETINOPATHY = 'DIABETIC_RETINOPATHY', 'Retinopatía diabética'
    DRY_EYE = 'DRY_EYE', 'Ojo seco'
    MACULAR_DEGENERATION = 'MACULAR_DEGENERATION', 'Degeneración macular'


class Subsidiary(models.Model):
    subsidiary_name = models.CharField(
        "Nombre Sucursal", max_length=30, blank=True)
    direction = models.CharField("Dirección", max_length=50, blank=True)
    phone = models.CharField("Telefono", max_length=23, blank=True)
    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.subsidiary_name


class Laboratory(models.Model):
    laboratory_name = models.CharField(
        "Laboratorio", max_length=40, null=False)
    direction = models.CharField("Dirección", max_length=50, blank=True)
    phone = models.CharField("Telefono", max_length=23, blank=True)
    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Laboratorio"
        verbose_name_plural = "Laboratorios"

    def __str__(self):
        return self.laboratory_name


class CrystalTreatments(models.Model):
    treatment_name = models.CharField("Nombre del tratamiento", max_length=50)
    description = models.TextField("Descripcion", blank=True)
    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"

    def __str__(self):
        return self.treatment_name


class CrystalMaterial(models.Model):

    material_name = models.CharField("Nombre del Material", max_length=50)
    refractive_index = models.DecimalField(
        "Indice de refracción", max_digits=4, decimal_places=3, blank=True, null=True)
    abbe = models.DecimalField(
        "Valor abbe", max_digits=3, decimal_places=1, blank=True, null=True)
    description = models.TextField("Descripcion", blank=True)
    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Material de la luna"
        verbose_name_plural = "Materiales de las lunas"

    def __str__(self):
        return self.material_name


class Crystal(models.Model):

    crystal_name = models.CharField("Nombre Luna", max_length=70)
    material = models.ForeignKey(
        CrystalMaterial, verbose_name="Material", on_delete=models.SET_NULL, null=True, blank=True)
    treatments = models.ManyToManyField(
        CrystalTreatments, verbose_name="Tratamientos", blank=True)
    default_price = models.DecimalField('Precio de los lentes', max_digits=10, decimal_places=2, validators=[
                                        MinValueValidator(0, 'No se permite el valor ingresado')], blank=True, null=True)
    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)

    class Meta:
        verbose_name = "Luna"
        verbose_name_plural = "Lunas"

    def __str__(self):
        return self.crystal_name

    def get_treatments(self):
        treatments = list(self.treatments.all())
        treatments = [treatment.treatment_name for treatment in treatments]
        if len(treatments) == 0:
            return "--"
        return ", ".join(treatments)


class Prescription(models.Model):
    class PrescriptionType(models.TextChoices):
        MONOFOCAL = 'MONOFOCAL', 'Monofocal'
        BIFOCAL = 'BIFOCAL', 'Bifocal'
        OCCUPATIONAL = 'OCCUPATIONAL', 'Ocupacional'
        PROGRESSIVE = 'PROGRESSIVE', 'Progressivo'

    @staticmethod
    def generateChoices(start, end):
        choices = [(decimal.Decimal(f'{i*0.25}0') if i % 2 == 0 else decimal.Decimal(f'{i*0.25}'), (f'{i*0.25}0' if i <=
                    0 else f'+{i*0.25}0') if i % 2 == 0 else (f'{i*0.25}' if i <= 0 else f'+{i*0.25}')) for i in range(end-1, start-1, -1)]
        for i, (value, name) in enumerate(choices):
            if value == decimal.Decimal(0):
                choices.insert(i, ('', '--'))
                break
        return choices

    spherical_choices = generateChoices.__func__(-100, 101)
    cylinder_choices = generateChoices.__func__(-40, 1)
    axis_choices = [(i, f'{i}°') for i in range(180, -1, -1)]
    axis_choices.append(('', '--'))
    dip_choices = [(i, f'{i}mm') for i in range(81, 40, -1)]
    dip_choices.append(('', '--'))
    dnp_choices = [(decimal.Decimal(f'{i/2}') if i % 2 == 0 else decimal.Decimal(
        f'{i/2}'), f'{i/2}mm' if i % 2 == 1 else f'{int(i/2)}mm') for i in range(81, 40, -1)]
    dnp_choices.append(('', '--'))
    add_choices = generateChoices.__func__(1, 25)
    add_choices.append(('', '--'))
    # print(colored(spherical_choices,'green'))
    # print(colored(cylinder_choices,'red'))
    # print(colored(axis_choices,'green'))
    # print(colored(dip_choices,'red'))
    # print(colored(add_choices,'green'))

    optic = models.ForeignKey(
        OpticUser, verbose_name="Optica", on_delete=models.CASCADE, null=False)
    is_dip = models.BooleanField('Dip o Dnp')
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT, verbose_name="Paciente")
    subsidiary = models.ForeignKey(
        Subsidiary, on_delete=models.SET_NULL, verbose_name="Sucursal", blank=True, null=True)
    laboratory = models.ForeignKey(
        Laboratory, verbose_name="Laboratorio", on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(
        Account, verbose_name="Doctor", on_delete=models.SET_NULL, blank=True, null=True)
    prescription_optic_id = models.PositiveIntegerField(blank=True)
    prescription_type = models.CharField(
        "Tipo", max_length=50, choices=PrescriptionType.choices, null=True, blank=True)
    date = models.DateField(verbose_name='Fecha', default=timezone.now)
    time = models.TimeField(verbose_name='Hora', default=timezone.now)
    far_spherical_right = models.DecimalField(
        "Esf. derecho Lejos", max_digits=4, decimal_places=2, blank=True, null=True, choices=spherical_choices)
    far_cylinder_right = models.DecimalField(
        "Cil. derecho Lejos", max_digits=4, decimal_places=2, blank=True, null=True, choices=cylinder_choices)
    far_axis_right = models.PositiveSmallIntegerField("Eje derecho Lejos", validators=[MaxValueValidator(
        180, 'El eje solo permite valores entre 0° y 180°')], blank=True, null=True, choices=axis_choices)
    far_av_right = models.CharField(
        "Av. derecho lejos", max_length=50, blank=True, null=True)
    far_dnp_right = models.DecimalField(
        "Dnp. derecho lejos", max_digits=3, decimal_places=1, blank=True, null=True, choices=dnp_choices)
    far_spherical_left = models.DecimalField(
        "Esf. izquierdo Lejos", max_digits=4, decimal_places=2, blank=True, null=True, choices=spherical_choices)
    far_cylinder_left = models.DecimalField(
        "Cil. izquierdo Lejos", max_digits=4, decimal_places=2, blank=True, null=True, choices=cylinder_choices)
    far_axis_left = models.PositiveSmallIntegerField("Eje izquierdo Lejos", validators=[MaxValueValidator(
        180, 'El eje solo permite valores entre 0° y 180°')], blank=True, null=True, choices=axis_choices)
    far_av_left = models.CharField(
        "Av. izquierdo lejos", max_length=50, blank=True, null=True)
    far_dnp_left = models.DecimalField(
        "Dnp. izquierdo lejos", max_digits=3, decimal_places=1, blank=True, null=True, choices=dnp_choices)
    intermediate_spherical_right = models.DecimalField(
        "Esf. derecho intermedio", max_digits=4, decimal_places=2, blank=True, null=True, choices=spherical_choices)
    intermediate_cylinder_right = models.DecimalField(
        "Cil. derecho intermedio", max_digits=4, decimal_places=2, blank=True, null=True, choices=cylinder_choices)
    intermediate_axis_right = models.PositiveSmallIntegerField("Eje derecho Lintermedio", validators=[MaxValueValidator(
        180, 'El eje solo permite valores entre 0° y 180°')], blank=True, null=True, choices=axis_choices)
    intermediate_av_right = models.CharField(
        "Av. derecho intermedio", max_length=50, blank=True, null=True)
    intermediate_dnp_right = models.DecimalField(
        "Dnp. derecho intermedio", max_digits=3, decimal_places=1, blank=True, null=True, choices=dnp_choices)
    intermediate_spherical_left = models.DecimalField(
        "Esf. izquierdo intermedio", max_digits=4, decimal_places=2, blank=True, null=True, choices=spherical_choices)
    intermediate_cylinder_left = models.DecimalField(
        "Cil. izquierdo intermedio", max_digits=4, decimal_places=2, blank=True, null=True, choices=cylinder_choices)
    intermediate_axis_left = models.PositiveSmallIntegerField("Eje izquierdo intermedio", validators=[MaxValueValidator(
        180, 'El eje solo permite valores entre 0° y 180°')], blank=True, null=True, choices=axis_choices)
    intermediate_av_left = models.CharField(
        "Av. izquierdo intermedio", max_length=50, blank=True, null=True)
    intermediate_dnp_left = models.DecimalField(
        "Dnp. izquierdo intermedio", max_digits=3, decimal_places=1, blank=True, null=True, choices=dnp_choices)
    near_spherical_right = models.DecimalField(
        "Esf. derecho Cerca", max_digits=4, decimal_places=2, blank=True, null=True, choices=spherical_choices)
    near_cylinder_right = models.DecimalField(
        "Cil. derecho Cerca", max_digits=4, decimal_places=2, blank=True, null=True, choices=cylinder_choices)
    near_axis_right = models.PositiveSmallIntegerField("Eje derecho Cerca", validators=[MaxValueValidator(
        180, 'El eje solo permite valores entre 0° y 180°')], blank=True, null=True, choices=axis_choices)
    near_av_right = models.CharField(
        "Av. derecho Cerca", max_length=50, blank=True, null=True)
    near_dnp_right = models.DecimalField(
        "Dnp. derecho Cerca", max_digits=3, decimal_places=1, blank=True, null=True, choices=dnp_choices)
    near_spherical_left = models.DecimalField(
        "Esf. izquierdo Cerca", max_digits=4, decimal_places=2, blank=True, null=True, choices=spherical_choices)
    near_cylinder_left = models.DecimalField(
        "Cil. izquierdo Cerca", max_digits=4, decimal_places=2, blank=True, null=True, choices=cylinder_choices)
    near_axis_left = models.PositiveSmallIntegerField("Eje izquierdo Cerca", validators=[MaxValueValidator(
        180, 'El eje solo permite valores entre 0 y 180')], blank=True, null=True, choices=axis_choices)
    near_av_left = models.CharField(
        "Av. izquierdo Cerca", max_length=50, blank=True, null=True)
    near_dnp_left = models.DecimalField(
        "Dnp. izquierdo Cerca", max_digits=3, decimal_places=1, blank=True, null=True, choices=dnp_choices)
    patient_notes = models.TextField("Notas para el paciente", blank=True)
    laboratory_notes = models.TextField(
        "Notas para el laboratorio", blank=True)
    optic_notes = models.TextField("Notas para tu optica", blank=True)
    intermediate_add = models.DecimalField(
        "Add. intermedio", max_digits=4, decimal_places=2, blank=True, null=True, choices=add_choices)
    near_add = models.DecimalField(
        "Add. cerca", max_digits=4, decimal_places=2, blank=True, null=True, choices=add_choices)
    diagnosis = models.CharField("Diagnostico", max_length=84, blank=True,
                                 help_text="Diagnostico del paciente según las medidas")
    measure_price = models.DecimalField('Precio de la medida', max_digits=10, decimal_places=2, default=0, validators=[
                                        MinValueValidator(0, 'No se permite el valor ingresado')], blank=True, null=True)
    crystals = models.ForeignKey(
        Crystal, on_delete=models.SET_NULL, verbose_name="Lunas", blank=True, null=True)
    crystals_cost = models.DecimalField('Costo de las lunas', max_digits=10, decimal_places=2, validators=[
        MinValueValidator(0, 'No se permite el valor ingresado')], blank=True, null=True)
    crystals_price = models.DecimalField('Precio de venta de las lunas', max_digits=10, decimal_places=2, validators=[
                                         MinValueValidator(0, 'No se permite el valor ingresado')], blank=True, null=True)
    frame = models.CharField("Descripcion de la montura",
                             max_length=120, null=True, blank=True)
    frame_price = models.DecimalField('Precio de venta de la montura', max_digits=10, decimal_places=2, validators=[
                                      MinValueValidator(0, 'No se permite el valor ingresado')], blank=True, null=True)

    class Meta:
        verbose_name = "Receta"
        verbose_name_plural = "Recetas"
        unique_together = ('optic', 'prescription_optic_id')

    def __str__(self):
        return f"""{self.patient}"""
        # ODL:{self.far_spherical_right if self.far_spherical_right is not None else '?'}({self.far_cylinder_right if self.far_cylinder_right is not None else '?'}){self.far_axis_right if self.far_axis_right is not None else '?'}°
        # OIL:{self.far_spherical_left if self.far_spherical_left is not None else '?'}({self.far_cylinder_left if self.far_cylinder_left is not None else '?'}){self.far_axis_left if self.far_axis_left is not None else '?'}°
        # ODC:{self.near_spherical_right if self.near_spherical_right is not None else '?'}({self.near_cylinder_right if self.near_cylinder_right is not None else '?'}){self.near_axis_right if self.near_axis_right is not None else '?'}°
        # OIC:{self.near_spherical_left if self.near_spherical_left is not None else '?'}({self.near_cylinder_left if self.near_cylinder_left is not None else '?'}){self.near_axis_left if self.near_axis_left is not None else '?'}°

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self._state.adding is True:
            optic = OpticUser.objects.get(pk=self.optic.id)
            last_prescription = optic.prescription_set.last()
            if last_prescription:
                prescription_optic_id = last_prescription.prescription_optic_id + 1
            else:
                prescription_optic_id = 1
            self.prescription_optic_id = prescription_optic_id
        near = self.has_near_table() or self.near_add is not None
        intermediate = self.has_intermediate_table() or self.intermediate_add is not None
        far = self.has_far_table()
        if isOnlyOneTrue(near, intermediate, far):
            self.prescription_type = Prescription.PrescriptionType.MONOFOCAL
        elif near and intermediate and far:
            self.prescription_type = Prescription.PrescriptionType.PROGRESSIVE
        elif near and intermediate:
            self.prescription_type = Prescription.PrescriptionType.OCCUPATIONAL
        elif (near and far) or (intermediate and far):
            self.prescription_type = Prescription.PrescriptionType.BIFOCAL
        else:
            self.prescription_type = None
        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)

    def get_total(self):
        if self.frame_price is None and self.crystals_price is None and self.measure_price is None:
            return None

        if self.frame_price is None:
            frame_price = 0
        else:
            frame_price = self.frame_price

        if self.crystals_price is None:
            crystals_price = 0
        else:
            crystals_price = self.crystals_price

        if self.measure_price is None:
            measure_price = 0
        else:
            measure_price = self.measure_price
        total = frame_price + crystals_price + measure_price
        return total

    def has_far_table(self):
        if (self.far_spherical_right is not None or self.far_cylinder_right is not None
            or self.far_axis_right is not None or self.far_av_right is not None or
            self.far_dnp_right is not None
            or self.far_spherical_left is not None or self.far_cylinder_left is not None
            or self.far_axis_left is not None or self.far_av_left is not None or
                self.far_dnp_left is not None):
            return True
        return False

    def has_intermediate_table(self):
        if (self.intermediate_spherical_right is not None or self.intermediate_cylinder_right is not None
            or self.intermediate_axis_right is not None or self.intermediate_av_right is not None or
            self.intermediate_dnp_right is not None
            or self.intermediate_spherical_left is not None or self.intermediate_cylinder_left is not None
            or self.intermediate_axis_left is not None or self.intermediate_av_left is not None or
                self.intermediate_dnp_left is not None):
            return True
        return False

    def has_near_table(self):
        if (self.near_spherical_right is not None or self.near_cylinder_right is not None
            or self.near_axis_right is not None or self.near_av_right is not None or
            self.near_dnp_right is not None
            or self.near_spherical_left is not None or self.near_cylinder_left is not None
            or self.near_axis_left is not None or self.near_av_left is not None or
                self.near_dnp_left is not None):
            return True
        return False
