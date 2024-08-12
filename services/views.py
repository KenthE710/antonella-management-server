from rest_framework import viewsets

from inventory.models import Producto
from .models import Servicio, ServicioRealizado, ServicioRealizadoProducto
from .serializers import (
    ServicioGridSerializer,
    ServicioRealizadoAllSerializer,
    ServicioSerializer,
    ServicioRealizadoSerializer,
    ServicioRealizadoProductoSerializer,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db import transaction


class ServicioView(viewsets.ModelViewSet):
    queryset = Servicio.objects.active().all()
    serializer_class = ServicioSerializer

    @action(methods=["get"], detail=False)
    def selector(self, request: Request):
        queryset = Servicio.objects.active().values("id", "nombre")
        return Response(queryset, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.select_related("encargado").prefetch_related("productos")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ServicioGridSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ServicioGridSerializer(queryset, many=True)
        return Response(serializer.data)


class ServicioRealizadoView(viewsets.ModelViewSet):
    queryset = ServicioRealizado.objects.active().all()
    serializer_class = ServicioRealizadoSerializer

    @action(methods=["get"], detail=True)
    def complete(self, request: Request, pk=None):
        return self.retrieve(request)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        return self.list(request)

    def get_serializer(self, *args, **kwargs):
        if self.action == "grid" or self.action == "complete":
            return ServicioRealizadoAllSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        ServicioRealizadoProducto.objects.filter(servicio_realizado=instance).delete()

    @transaction.atomic
    def perform_create(self, serializer):
        servicioRealizado = serializer.save()
        if self.request.data["productos"]:
            producto_data = {
                item["producto"]: item["cantidad"]
                for item in self.request.data["productos"]
            }
            productos = Producto.objects.filter(id__in=producto_data.keys())

            for producto in productos:
                cantidad = producto_data.get(producto.id, 1)

                if cantidad < 1:
                    raise Exception(
                        f"La cantidad del producto {producto.nombre} debe ser mayor a 0"
                    )
                if producto.usos_restantes < cantidad:
                    raise Exception(
                        f"El producto {producto.nombre} no tiene suficiente stock"
                    )

                while cantidad > 0:
                    loteToUse = producto.getLoteToUse
                    if loteToUse is None:
                        raise Exception(
                            f"El producto {producto.nombre} no tiene lotes disponibles"
                        )

                    if cantidad <= loteToUse.servicios_restantes:
                        ServicioRealizadoProducto.objects.create(
                            servicio_realizado=servicioRealizado,
                            producto=producto,
                            lote=loteToUse,
                            cantidad=cantidad,
                        )
                        cantidad = 0
                    else:
                        ServicioRealizadoProducto.objects.create(
                            servicio_realizado=servicioRealizado,
                            producto=producto,
                            lote=loteToUse,
                            cantidad=loteToUse.servicios_restantes,
                        )
                        cantidad -= loteToUse.servicios_restantes

    """ def perform_update(self, serializer):
        instance = serializer.save()
        if self.request.data["productos"]:
            producto_data = {
                item["producto"]: item["cantidad"]
                for item in self.request.data["productos"]
            }
            productos = Producto.objects.filter(id__in=producto_data.keys())

            for producto in productos:
                cantidad = producto_data.get(producto.id, 1)
                if cantidad < 1:
                    raise Exception(
                        f"La cantidad del producto {producto.nombre} debe ser mayor a 0"
                    )
                
                servicioRealizadoProductos = ServicioRealizadoProducto.objects.filter(
                    producto=producto, servicio_realizado=instance
                ).all()
                
                for srp in servicioRealizadoProductos:
                    cantidad -= srp.cantidad
                    
                if cantidad < 0:
                    raise Exception(
                        f"La cantidad del producto {producto.nombre} no puede ser menor a la cantidad ya registrada"
                    )
                if cantidad > producto.usos_restantes:
                    raise Exception(
                        f"El producto {producto.nombre} no tiene suficientes existencias para la cantidad solicitada"
                    )
                    
                lastedServicioRealizadoProducto = ServicioRealizadoProducto.objects.filter(
                    producto=producto, servicio_realizado=instance
                ).last()
                
                if lastedServicioRealizadoProducto and not lastedServicioRealizadoProducto.lote.consumido:
                    

                if servicioRealizadoProducto:
                    if servicioRealizadoProducto.cantidad == cantidad:
                        continue

                    cantidad_diferencia = cantidad - servicioRealizadoProducto.cantidad

                    if cantidad_diferencia > producto.usos_restantes:
                        raise Exception(
                            f"El producto {producto.nombre} no tiene suficientes existencias para la cantidad solicitada"
                        )

                    if (
                        cantidad_diferencia
                        <= servicioRealizadoProducto.lote.servicios_restantes
                    ):
                        servicioRealizadoProducto.cantidad = (
                            servicioRealizadoProducto.cantidad + cantidad_diferencia
                        )
                        servicioRealizadoProducto.save()
                    else:
                        servicioRealizadoProducto.cantidad = (
                            servicioRealizadoProducto.cantidad
                            + servicioRealizadoProducto.lote.servicios_restantes
                        )
                        servicioRealizadoProducto.save()

                        cantidad_falta = (
                            cantidad_diferencia
                            - servicioRealizadoProducto.lote.servicios_restantes
                        )

                        while cantidad_falta > 0:
                            new_lote = producto.getLoteToUse
                            if new_lote is None:
                                raise Exception(
                                    f"El producto {producto.nombre} no tiene lotes disponibles"
                                )

                            if cantidad_falta <= new_lote.servicios_restantes:
                                ServicioRealizadoProducto.objects.create(
                                    servicio_realizado=instance,
                                    producto=producto,
                                    lote=new_lote,
                                    cantidad=cantidad_falta,
                                )
                                cantidad_falta = 0
                            else:
                                ServicioRealizadoProducto.objects.create(
                                    servicio_realizado=instance,
                                    producto=producto,
                                    lote=new_lote,
                                    cantidad=new_lote.servicios_restantes,
                                )
                                cantidad_falta = (
                                    cantidad_falta - new_lote.servicios_restantes
                                )
                else:
                    if producto.usos_restantes < cantidad:
                        raise Exception(
                            f"El producto {producto.nombre} no tiene suficiente stock"
                        )

                    loteToUse = producto.getLoteToUse
                    if loteToUse is None:
                        raise Exception(
                            f"El producto {producto.nombre} no tiene lotes disponibles"
                        )

                    ServicioRealizadoProducto.objects.create(
                        servicio_realizado=instance,
                        producto=producto,
                        lote=loteToUse,
                        cantidad=cantidad,
                    ) """


class ServicioRealizadoProductoView(viewsets.ModelViewSet):
    queryset = ServicioRealizadoProducto.objects.active().all()
    serializer_class = ServicioRealizadoProductoSerializer

    @action(
        methods=["get"],
        detail=False,
        url_path="by_servicio_realizado/(?P<servicio_realizado_id>[^/.]+)",
    )
    def by_servicio_realizado(self, request: Request, servicio_realizado_id=None):
        queryset = ServicioRealizadoProducto.objects.active().filter(
            servicio_realizado=servicio_realizado_id
        )
        serializer = ServicioRealizadoProductoSerializer(queryset, many=True)
        return Response(serializer.data)
