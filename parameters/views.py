from django.shortcuts import render
from rest_framework import viewsets
from .models import Parametro
from .serializers import ParametroSerializer

class ParametroView(viewsets.ModelViewSet):
    queryset = Parametro.objects.all()
    serializer_class = ParametroSerializer