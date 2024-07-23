from django.shortcuts import render
from rest_framework import viewsets
from .models import Servicio
from .serializers import ServicioSerializer

class ServicioView(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer