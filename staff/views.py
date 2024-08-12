from django.shortcuts import render
from rest_framework import viewsets
from .models import Personal
from .serializers import PersonalSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from django.db.models import Q


class PersonalView(viewsets.ModelViewSet):
    queryset = Personal.objects.active().all()
    serializer_class = PersonalSerializer

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        return self.list(request)

    @action(methods=["get"], detail=False)
    def search(self, request: Request):
        query = request.query_params.get("q", "")
        queryset = self.get_queryset().filter(
            Q(nombre__icontains=query)
            | Q(apellido__icontains=query)
            | Q(cedula__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
