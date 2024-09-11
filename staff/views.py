from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q

from .models import Personal, PersonalState
from .serializers import (
    PersonalSerializer,
    PersonalStateSerializer,
    PersonalFullSerializer,
)


class PersonalView(viewsets.ModelViewSet):
    queryset = Personal.objects.active().all()
    serializer_class = PersonalSerializer

    @action(methods=["get"], detail=True)
    def complete(self, request: Request, pk=None):
        return self.retrieve(request)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        queryset = self.filter_queryset(self.get_queryset())

        strCedula = request.query_params.get("cedula")
        strNombre = request.query_params.get("nombre")
        strApellido = request.query_params.get("apellido")
        strEmail = request.query_params.get("email")
        strStates = request.query_params.get("state")

        if strCedula:
            queryset = queryset.filter(cedula__icontains=strCedula)
        if strNombre:
            queryset = queryset.filter(nombre__icontains=strNombre)
        if strApellido:
            queryset = queryset.filter(apellido__icontains=strApellido)
        if strEmail:
            queryset = queryset.filter(email__icontains=strEmail)
        if strStates:
            arrayStates = Q()
            for strState in strStates.split(","):
                arrayStates |= Q(estado__name=strState)
                
            queryset = queryset.filter(arrayStates)

        page = self.paginate_queryset(queryset)
        if hasOffset and page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data

            if isinstance(self.paginator, LimitOffsetPagination):
                offset = int(self.paginator.get_offset(request))

                for i, item in enumerate(data):
                    item["row_number"] = int(offset) + (i + 1)

            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": len(serializer.data), "results": serializer.data})

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

    @action(methods=["get"], detail=False)
    def state(self, request: Request):
        states = PersonalState.objects.active().all()
        serializer = PersonalStateSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer(self, *args, **kwargs):
        if self.action == "grid" or self.action == "complete":
            return PersonalFullSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
