from django.db.models import ProtectedError
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from datetime import datetime, timedelta
import calendar as c

from django.db.models import Count
from django.db.models.functions import (ExtractDay, ExtractMonth, ExtractQuarter, ExtractWeek,ExtractIsoWeekDay, ExtractWeekDay, ExtractIsoYear, ExtractYear)

from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    DestroyAPIView,
    UpdateAPIView,  # no trae los datos del paciente
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .functions import monthdelta, Day, Week, Month, Year, Hour,Dayname
from .models import Patient, Prescription,Subsidiary
from .serializers import PatientSerializer, PrescriptionSerializer,SubsidiaryPrescriptionSerializer


MESES = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
         7: 'Julio', 8: 'Agosto', 9: 'Setiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}


class PatientListApiView(ListAPIView):
    """ api para enviar un paciente con el id dado"""
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Patient.objects.all()


class PatientCreateApiView(CreateAPIView):
    """ api para crear un paciente """
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer


class PatientDetailApiView(RetrieveAPIView):
    """ api para mostrar el detalle de un pacientev"""
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()


class PatientDeleteApiView(DestroyAPIView):
    """ api para eliminar un paciente"""
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()

    def perform_destroy(self, instance):
        try:
            super().perform_destroy(instance)
        except ProtectedError as e:
            raise serializers.ValidationError({"error":"El paciente tiene prescripciones"})

class PatientUpdateApiWiew(RetrieveUpdateAPIView):
    """ api para modificar un paciente"""
    permission_classes = [IsAuthenticated]
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()


class ReportPrescriptionCount(ListAPIView):
    """ reporte de prescripciones por dia,semana,mes y año """

    permission_classes = [IsAuthenticated]
    serializer_class = PrescriptionSerializer
    current = None
    current_year = None
    current_month = None
    label = None
    size=None

    def get_queryset(self):

        calendar = self.request.GET.get('calendar', '')
        actual = self.request.GET.get('current', None)
        option = self.request.GET.get('option', '')
        hoy = datetime.today()
        optica=self.request.user.get_opticuser()

        if(calendar == 'month'):
            self.label = 'Mes'
            if not actual:
                self.current_year = hoy.year
                self.current = MESES[hoy.month]

            else:
                self.current_year = int(
                    self.request.GET.get('current_year', None))
                actual_num = list(MESES.keys())[list(MESES.values()).index(actual)]

                if option == 'next':
                    if not (actual_num+1 > hoy.month and self.current_year == hoy.year):
                        if actual_num+1 <= 12:
                            self.current = MESES[actual_num+1]
                        else:
                            if self.current_year+1 <= hoy.year:
                                self.current = MESES[1]
                                self.current_year += 1
                            else:
                                self.current = MESES[actual_num]
                    else:
                        self.current = MESES[actual_num]
                elif option == 'previus':
                    if actual_num-1 > 0:
                        self.current = MESES[actual_num-1]
                    else:
                        self.current = MESES[12]
                        self.current_year -= 1
            self.size= c.monthrange(self.current_year, list(MESES.keys())[list(MESES.values()).index(self.current)])[1]
            query = Prescription.objects.filter(optic=optica,date__month=list(MESES.keys())[list(MESES.values()).index(self.current)], date__year=self.current_year).annotate(
                dato=Day('date')).values('dato').annotate(total=Count('date')).order_by('dato')
        elif calendar == 'year':
            self.size=12
            self.label = 'Año'
            if not actual:
                self.current = hoy.year
            else:
                if option == 'next':
                    if int(actual)+1 <= hoy.year:
                        self.current = int(actual)+1
                    else:
                        self.current = hoy.year
                elif option == 'previus':
                    self.current = int(actual)-1

            query = Prescription.objects.filter(optic=optica,date__year=self.current).annotate(dato=Month(
                'date')).values('dato').annotate(total=Count('date')).order_by('dato')
        elif calendar == 'week':
            self.size=7
            self.label = 'Semana'
            if not actual:
                self.current =hoy.isocalendar().week #int(hoy.strftime('%W'))
                self.current_year = hoy.year
            else:
                self.current_year = int(self.request.GET.get('current_year', None))
                self.current = int(actual)
                if option == 'next':
                    if not (self.current+1 > hoy.isocalendar().week and self.current_year == hoy.year):
                        if self.current+1 <= 53:
                            self.current += 1
                        else:
                            self.current = 1
                            self.current_year += 1
                    else:
                        self.current = hoy.isocalendar().week
                elif option == 'previus':
                    if self.current-1 > 0:
                        self.current -= 1
                    else:
                        self.current = 53
                        self.current_year -= 1
            query = Prescription.objects.filter(optic=optica,date__week=self.current, date__year=self.current_year).annotate(
                dato=ExtractIsoWeekDay('date')).values('dato').annotate(total=Count('date')).order_by('dato')
            query2 = Prescription.objects.filter(optic=optica,date__week=self.current, date__year=self.current_year).annotate(
                dato=ExtractIsoWeekDay('date')).values('dato','date__iso_week_day')
            print("lllllllllllllllllllllllll",query2)    
            for i in query2 :
                print(i)
        elif calendar == 'day':
            self.size=24
            self.label = 'Dia'
            if not actual:
                self.current = hoy.day
                self.current_year = hoy.year
                self.current_month = hoy.month
            else:
                self.current_year = int(
                    self.request.GET.get('current_year', None))
                self.current = int(actual)
                self.current_month = int(
                    self.request.GET.get('current_month', None))
                cant_dias_mes = c.monthrange(self.current_year, self.current_month)[1]
                if option == 'next':
                    if not (self.current+1 > hoy.day and self.current == hoy.day):
                        if self.current+1 <= cant_dias_mes:
                            self.current += 1
                        else:
                            if self.current_month+1 <= 12:
                                self.current_month += 1
                            else:
                                self.current_month = 1
                                self.current_year += 1
                            self.current = 1
                elif option == 'previus':
                    if self.current-1 > 0:
                        self.current -= 1
                    else:
                        if self.current_month-1 > 0:
                            self.current_month -= 1
                        else:
                            self.current_month = 12
                            self.current_year -= 1
                        self.current = c.monthrange(
                            self.current_year, self.current_month)[1]

            query = Prescription.objects.filter(optic=optica,date__day=self.current, date__year=self.current_year,date__month=self.current_month).annotate(dato=Hour(
                'time')).values('dato').annotate(total=Count('time')).order_by('dato')

        return query

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        op=self.request.GET.get('option','')
        new = {
            'current': self.current,
            'current_year': self.current_year,
            'current_month': self.current_month,
            'label': self.label,
            'size':self.size,
        }
        data = {'data': serializer.data, 'options': new}
        return Response(data)

class ReportSubsidiaryPrescription(ListAPIView):
    """ reporte de prescripciones de las subsidiarias por dia,semana,mes y año """

    permission_classes = [IsAuthenticated]
    serializer_class = SubsidiaryPrescriptionSerializer
    current = None
    current_year = None
    current_month = None
    label = None
    size=None
    subsididiary=None

    def get_queryset(self):

        calendar = self.request.GET.get('calendar', '')
        actual = self.request.GET.get('current', None)
        option = self.request.GET.get('option', '')
        hoy = datetime.today()
        optica=self.request.user.get_opticuser()
        self.subsididiary=Prescription.objects.filter(optic=optica).distinct('subsidiary_id').values('subsidiary__subsidiary_name')


        if(calendar == 'month'):
            self.label = 'Mes'
            if not actual:
                self.current_year = hoy.year
                self.current = MESES[hoy.month]

            else:
                self.current_year = int(
                    self.request.GET.get('current_year', None))
                actual_num = list(MESES.keys())[list(MESES.values()).index(actual)]

                if option == 'next':
                    if not (actual_num+1 > hoy.month and self.current_year == hoy.year):
                        if actual_num+1 <= 12:
                            self.current = MESES[actual_num+1]
                        else:
                            if self.current_year+1 <= hoy.year:
                                self.current = MESES[1]
                                self.current_year += 1
                            else:
                                self.current = MESES[actual_num]
                    else:
                        self.current = MESES[actual_num]
                elif option == 'previus':
                    if actual_num-1 > 0:
                        self.current = MESES[actual_num-1]
                    else:
                        self.current = MESES[12]
                        self.current_year -= 1
            self.size= c.monthrange(self.current_year, list(MESES.keys())[list(MESES.values()).index(self.current)])[1]
            query = Prescription.objects.filter(optic=optica,date__month=list(MESES.keys())[list(MESES.values()).index(self.current)], date__year=self.current_year).annotate(dato=Day('date')).values('subsidiary','dato').annotate(total =Count('id')).order_by('dato')

           
        elif calendar == 'year':
            self.size=12
            self.label = 'Año'
            if not actual:
                self.current = hoy.year
            else:
                if option == 'next':
                    if int(actual)+1 <= hoy.year:
                        self.current = int(actual)+1
                    else:
                        self.current = hoy.year
                elif option == 'previus':
                    self.current = int(actual)-1

            query = Prescription.objects.filter(optic=optica,date__year=self.current).annotate(dato=Month(
                'date')).values('subsidiary','dato').annotate(total=Count('id')).order_by('dato')
        elif calendar == 'week':
            self.size=7
            self.label = 'Semana'
            if not actual:
                self.current =hoy.isocalendar().week #int(hoy.strftime('%W'))
                self.current_year = hoy.year
            else:
                self.current_year = int(self.request.GET.get('current_year', None))
                self.current = int(actual)
                if option == 'next':
                    if not (self.current+1 > hoy.isocalendar().week and self.current_year == hoy.year):
                        if self.current+1 <= 53:
                            self.current += 1
                        else:
                            self.current = 1
                            self.current_year += 1
                    else:
                        self.current = hoy.isocalendar().week
                elif option == 'previus':
                    if self.current-1 > 0:
                        self.current -= 1
                    else:
                        self.current = 53
                        self.current_year -= 1
            query = Prescription.objects.filter(optic=optica,date__week=self.current, date__year=self.current_year).annotate(
                dato=ExtractIsoWeekDay('date')).values('subsidiary','dato').annotate(total=Count('id')).order_by('dato')
            
        elif calendar == 'day':
            self.size=24
            self.label = 'Dia'
            if not actual:
                self.current = hoy.day
                self.current_year = hoy.year
                self.current_month = hoy.month
            else:
                self.current_year = int(
                    self.request.GET.get('current_year', None))
                self.current = int(actual)
                self.current_month = int(
                    self.request.GET.get('current_month', None))
                cant_dias_mes = c.monthrange(self.current_year, self.current_month)[1]
                if option == 'next':
                    if not (self.current+1 > hoy.day and self.current == hoy.day):
                        if self.current+1 <= cant_dias_mes:
                            self.current += 1
                        else:
                            if self.current_month+1 <= 12:
                                self.current_month += 1
                            else:
                                self.current_month = 1
                                self.current_year += 1
                            self.current = 1
                elif option == 'previus':
                    if self.current-1 > 0:
                        self.current -= 1
                    else:
                        if self.current_month-1 > 0:
                            self.current_month -= 1
                        else:
                            self.current_month = 12
                            self.current_year -= 1
                        self.current = c.monthrange(
                            self.current_year, self.current_month)[1]

            query = Prescription.objects.filter(optic=optica,date__day=self.current, date__year=self.current_year,date__month=self.current_month).annotate(dato=Hour(
                'time')).values('subsidiary','dato').annotate(total=Count('id')).order_by('dato')

        return query

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        op=self.request.GET.get('option','')
        new = {
            'current': self.current,
            'current_year': self.current_year,
            'current_month': self.current_month,
            'label': self.label,
            'size':self.size,
            'subsididiary':self.subsididiary
        }
        data = {'data': serializer.data, 'options': new}
        return Response(data)
