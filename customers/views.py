from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Cliente
from .serializers import ClienteSerializer
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models.manager import BaseManager


class ClienteView(viewsets.ModelViewSet):
    queryset = Cliente.objects.active().all()
    serializer_class = ClienteSerializer

    @action(methods=["get"], detail=False)
    def selector(self, request: Request):
        queryset = Cliente.objects.active().values("id", "nombre", "apellido")
        return Response(queryset, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        queryset: BaseManager[Cliente] = Cliente.objects.active().all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(
            {"msg": "No se pudo paginar el resultado"},
            status=status.HTTP_400_BAD_REQUEST,
        )
