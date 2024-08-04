from rest_framework import viewsets
from .models import Servicio
from .serializers import ServicioGridSerializer, ServicioSerializer
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action


class ServicioView(viewsets.ModelViewSet):
    queryset = Servicio.objects.active().all()
    serializer_class = ServicioSerializer

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ServicioGridSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ServicioGridSerializer(queryset, many=True)
        return Response(serializer.data)
