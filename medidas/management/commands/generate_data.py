import random

from django.db import transaction
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import DataError

from medidas.models import Patient, Prescription, Subsidiary
from users.models import Account
from medidas.factories import (
    PatientFactory,
    PrescriptionFactory,
    SubsidiaryFactory,
)

USERNAME = 'pajason2000@gmail.com'
NUM_PATIENTS = 500
NUM_PRESCRIPTIONS = 5000
NUM_SUBSIDIARYS = 6

class Command(BaseCommand):
    help = "Generates test data"

    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models = [Prescription, Patient, Subsidiary,]
        account = Account.objects.get(username=USERNAME)
        optic = account.get_opticuser()
        for model in models:
            model.objects.filter(optic=optic).delete()
        self.stdout.write("Creating new data...")
        # Create all the patients
        patients = []
        for _ in range(NUM_PATIENTS):
            try:
                patient = PatientFactory(optic=optic)
                patients.append(patient)
            except DataError:
                print('DataError')

        # Create all the subsidiarys
        subsidiarys = []
        for _ in range(NUM_SUBSIDIARYS):
            try:
                subsidiary = SubsidiaryFactory(optic=optic)
                subsidiarys.append(subsidiary)
            except:
                print('ve')
        
        # Create all the prescriptions
        for _ in range(NUM_PRESCRIPTIONS):
            patient = random.choice(patients)
            subsidiary = random.choice(subsidiarys)
            try:
                prescription = PrescriptionFactory(subsidiary=subsidiary,optic=optic,patient=patient, is_dip=True)
                print(f'{_/NUM_PRESCRIPTIONS*100}%')
            except ValidationError:
                print('ValidationError')
            except ValueError:
                print('ValueError')