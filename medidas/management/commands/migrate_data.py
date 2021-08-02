from django.core.management.base import BaseCommand
from medidas.models import Patient, Prescription, Subsidiary
from users.models import Account
from django.conf import settings
import json

USERNAME = 'techi211706@hotmail.com'
FILE = settings.BASE_DIR.joinpath('migrate.json')


class Command(BaseCommand):
    help = "migrate existing data from olddatabase to this one"

    def handle(self, *args, **kwargs):
        self.stdout.write(f"migrating data...{FILE}")

        with open("migrate.json", "rb") as read_file:
            datas = json.load(read_file)

        account = Account.objects.get(username=USERNAME)
        optic = account.get_opticuser()
        subsidiary = optic.subsidiary_set.last()

        for data in datas:
            new_data = data["fields"]
            patient = Patient.objects.create(
                optic=optic, full_name=new_data["full_name"]
            )
            new_data.pop('full_name', None)
            dip = new_data.pop('dip', None)
            if dip:
                dip = float(dip)
            if new_data["date"] is None:
                new_data.pop('date')
            if new_data["patient_notes"] is None:
                new_data.pop('patient_notes')
            print(new_data)
            prescription = Prescription(
                optic=optic, patient=patient, subsidiary=subsidiary, is_dip=True, **new_data
            )
            if dip:
                if prescription.has_far_table():
                    prescription.far_dnp_right = dip/2
                    prescription.far_dnp_left = dip/2
                if prescription.has_near_table():
                    prescription.near_dnp_right = dip/2
                    prescription.near_dnp_left = dip/2
            prescription.save()
            print(prescription)
            print(f"far:{prescription.has_far_table()},intermediate:{prescription.has_intermediate_table()},near:{prescription.has_near_table()}")
