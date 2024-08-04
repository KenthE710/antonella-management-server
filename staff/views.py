from django.shortcuts import render
from rest_framework import viewsets
from .models import Personal
from .serializers import PersonalSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request


class PersonalView(viewsets.ModelViewSet):
    queryset = Personal.objects.active().all()
    serializer_class = PersonalSerializer

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        return self.list(request)
