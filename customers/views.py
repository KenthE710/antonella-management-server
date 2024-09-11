from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .models import Cliente
from .serializers import ClienteSerializer


class ClienteView(viewsets.ModelViewSet):
    queryset = Cliente.objects.active().all()
    serializer_class = ClienteSerializer

    @action(methods=["get"], detail=True)
    def complete(self, request: Request, pk=None):
        return self.retrieve(request)

    @action(methods=["get"], detail=False)
    def selector(self, request: Request):
        queryset = Cliente.objects.active().values("id", "nombre", "apellido")
        return Response(queryset, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        queryset = self.filter_queryset(self.get_queryset())
        
        strCedula = request.query_params.get("cedula")
        strNombre = request.query_params.get("nombre")
        strApellido = request.query_params.get("apellido")
        strEmail = request.query_params.get("email")
        strTelefono = request.query_params.get("telefono")
        
        if strCedula:
            queryset = queryset.filter(cedula__icontains=strCedula)
        if strNombre:
            queryset = queryset.filter(nombre__icontains=strNombre)
        if strApellido:
            queryset = queryset.filter(apellido__icontains=strApellido)
        if strEmail:
            queryset = queryset.filter(email__icontains=strEmail)
        if strTelefono:
            queryset = queryset.filter(telefono__icontains=strTelefono)

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
