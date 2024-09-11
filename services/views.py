import calendar
import datetime
from decimal import Decimal
from dateutil import parser
from django.db import transaction
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


from inventory.models import Producto
from .models import (
    Servicio,
    ServicioRealizado,
    ServicioRealizadoProducto,
    ServicioEstado,
    ServicioImg,
)
from .serializers import (
    ServicioGridSerializer,
    ServicioRealizadoAllSerializer,
    ServicioSerializer,
    ServicioRealizadoSerializer,
    ServicioRealizadoProductoSerializer,
    ServicioEstadoSimpleSerializer,
    ServicioImgSerializer,
    ServicioViewSerializer,
)


@permission_classes([AllowAny])
class ServicioView(viewsets.ModelViewSet):
    queryset = Servicio.objects.active().all()
    serializer_class = ServicioSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if "productos" in request.data and len(request.data["productos"]) == 0:
            instance.productos.clear()
            request.data.pop("productos")

        return super().update(request, *args, **kwargs)

    @action(methods=["get"], detail=False)
    def selector(self, request: Request):
        queryset = Servicio.objects.active().values("id", "nombre")
        return Response(queryset, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def state(self, request: Request):
        states = ServicioEstado.objects.active().all()
        serializer = ServicioEstadoSimpleSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        queryset = self.filter_queryset(self.get_queryset())
        queryset = (
            queryset.select_related("encargado", "estado")
            .prefetch_related("productos")
            .prefetch_cover()
            .with_disponibilidad()
        )

        strNombre = request.query_params.get("nombre")
        strDescripcion = request.query_params.get("descripcion")
        strPrecio = request.query_params.get("precio")
        strTiempoEst = request.query_params.get("tiempo_est")
        strEncargado = request.query_params.get("encargado")
        strProductos = request.query_params.get("productos")
        strDisponibilidad = request.query_params.get("disponibilidad")
        strState = request.query_params.get("state")

        if strNombre:
            queryset = queryset.filter(nombre__icontains=strNombre)
        if strDescripcion:
            queryset = queryset.filter(descripcion__icontains=strDescripcion)
        if strPrecio:
            queryset = queryset.filter(precio=Decimal(strPrecio))
        if strTiempoEst:
            queryset = queryset.filter(tiempo_est__icontains=strTiempoEst)
        if strEncargado:
            queryset = queryset.filter(encargado__nombre__icontains=strEncargado)
        if strProductos:
            queryset = queryset.filter(
                Q(productos__nombre__icontains=strProductos)
                | Q(productos__sku__icontains=strProductos)
            )
        if strDisponibilidad:
            queryset = queryset.filter(disponibilidad=strDisponibilidad == "true")
        if strState:
            queryset = queryset.filter(estado__nombre__icontains=strState)

        page = self.paginate_queryset(queryset)
        if hasOffset and page is not None:
            serializer = ServicioGridSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            data = serializer.data

            if isinstance(self.paginator, LimitOffsetPagination):
                offset = int(self.paginator.get_offset(request))

                for i, item in enumerate(data):
                    item["row_number"] = int(offset) + (i + 1)

            return self.get_paginated_response(data)

        serializer = ServicioGridSerializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response({"count": len(serializer.data), "results": serializer.data})

    @action(methods=["get"], detail=True)
    def view(self, request: Request, pk=None):
        servicio = self.get_object()
        serializer = ServicioViewSerializer(servicio)
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def delete_batch(self, request):
        ids = request.data.get("ids")
        if not ids:
            return Response(
                {"error": "Debe enviar una lista de IDs a eliminar"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Servicio.objects.active().filter(pk__in=ids)
        queryset.delete()
        return Response(status=status.HTTP_200_OK)


class ServicioRealizadoView(viewsets.ModelViewSet):
    queryset = ServicioRealizado.objects.active().all()
    serializer_class = ServicioRealizadoSerializer

    @action(methods=["get"], detail=True)
    def complete(self, request: Request, pk=None):
        return self.retrieve(request)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        queryset = self.filter_queryset(self.get_queryset())
        
        strServicio = request.query_params.get("servicio")
        strCliente = request.query_params.get("cliente")
        strFechaInicio = request.query_params.get("fecha_inicio")
        strFechaFin = request.query_params.get("fecha_fin")
        strPagado = request.query_params.get("pagado")
        strFinalizado = request.query_params.get("finalizado")
        
        if strServicio:
            queryset = queryset.filter(servicio__nombre__icontains=strServicio)
        if strCliente:
            queryset = queryset.filter(cliente__nombre__icontains=strCliente)
        if strPagado:
            queryset = queryset.filter(pagado=Decimal(strPagado))
        if strFinalizado:
            queryset = queryset.filter(finalizado=strFinalizado == "true")
        if strFechaInicio and strFechaFin:
            DateFechaInicio = parser.isoparse(strFechaInicio)
            DateFechaFin = parser.isoparse(strFechaFin)
            
            if DateFechaInicio > DateFechaFin:
                return Response(
                    {"error": "La fecha de inicio no puede ser mayor a la fecha de fin"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            queryset = queryset.filter(fecha__range=[DateFechaInicio, DateFechaFin])

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

    def get_serializer(self, *args, **kwargs):
        if self.action == "grid" or self.action == "complete":
            return ServicioRealizadoAllSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        ServicioRealizadoProducto.objects.filter(servicio_realizado=instance).delete()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

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
                if producto.get_usos_restantes < cantidad:
                    raise Exception(
                        f"El producto {producto.nombre} no tiene suficiente stock"
                    )

                while cantidad > 0:
                    loteToUse = producto.get_lote_to_use
                    if loteToUse is None:
                        raise Exception(
                            f"El producto {producto.nombre} no tiene lotes disponibles"
                        )

                    if cantidad <= loteToUse.get_servicios_restantes:
                        ServicioRealizadoProducto.objects.create(
                            servicio_realizado=servicioRealizado,
                            producto=producto,
                            lote=loteToUse,
                            cantidad=cantidad,
                        )
                        cantidad = 0
                    else:
                        srvRealizado = ServicioRealizadoProducto.objects.create(
                            servicio_realizado=servicioRealizado,
                            producto=producto,
                            lote=loteToUse,
                            cantidad=loteToUse.get_servicios_restantes,
                        )
                        cantidad -= srvRealizado.cantidad

    @action(methods=["post"], detail=False)
    def update_finalizado_batch(self, request):
        ids = request.data.get("ids")
        finalizado = request.data.get("finalizado")

        if not ids:
            return Response(
                {"error": "Debe enviar una lista de IDs a finalizar"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(ids) == 0:
            return Response(
                {"error": "La lista de IDs no puede estar vacía"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if finalizado is None:
            return Response(
                {"error": "Debe enviar el estado finalizado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = ServicioRealizado.objects.active().filter(pk__in=ids)
        queryset.update(finalizado=finalizado)
        return Response(status=status.HTTP_200_OK)


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


class ServicioImgView(viewsets.ModelViewSet):
    queryset = ServicioImg.objects.active().all()
    serializer_class = ServicioImgSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(
        methods=["get"],
        detail=False,
        url_path="by_servicio/(?P<servicio_id>[^/.]+)",
    )
    def by_servicio(self, request: Request, servicio_id=None):
        queryset = self.filter_queryset(self.get_queryset()).filter(
            servicio=servicio_id
        )
        serializer = self.get_serializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def assign_servicio(self, request: Request):
        servicio_id = request.data.get("servicio_id")
        imgs_id = request.data.get("imgs_id")

        if not servicio_id or not imgs_id:
            return Response(
                {"error": "Debe enviar el id del servicio y el id de la imagen"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(imgs_id, list):
            return Response(
                {"error": "imgs_id debe ser una lista de IDs de imágenes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        servicio = Servicio.objects.active().get(pk=servicio_id)

        for img in ServicioImg.objects.active().filter(pk__in=imgs_id):
            img.servicio = servicio
            img.is_tmp = False
            img.save()

        return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def service_per_months(request: Request):
    period = request.query_params.get("period", "month")

    ahora = timezone.now()

    if period == "week":
        # Agrupar por semana
        servicios = (
            ServicioRealizado.objects.active()
            .filter(fecha__year=ahora.year)
            .annotate(period=TruncWeek("fecha"))
            .values("period")
            .annotate(total_servicios=Count("id"))
            .order_by("period")
        )

    elif period == "month":
        # Agrupar por mes
        servicios = (
            ServicioRealizado.objects.active()
            .filter(fecha__year=ahora.year)
            .annotate(period=TruncMonth("fecha"))
            .values("period")
            .annotate(total_servicios=Count("id"))
            .order_by("period")
        )

    elif period == "year":
        # Agrupar por año
        servicios = (
            ServicioRealizado.objects.active()
            .annotate(period=TruncYear("fecha"))
            .values("period")
            .annotate(total_servicios=Count("id"))
            .order_by("period")
        )

    else:
        return Response(
            {"error": "Periodo no válido, use 'week', 'month' o 'year'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(servicios, status=status.HTTP_200_OK)


@api_view(["GET"])
def most_performed_services(request: Request):
    period = request.query_params.get("period", "month")
    strLimit = request.query_params.get("limit")

    today = timezone.now()
    today_date = today.date()

    if period == "week":
        start_date = today_date - datetime.timedelta(days=today_date.weekday())
        end_date = datetime.datetime.combine(start_date + datetime.timedelta(days=6), datetime.time.max)
    elif period == "month":
        start_date = today_date.replace(day=1)
        end_date = datetime.datetime.combine(today_date.replace(day=calendar.monthrange(today_date.year, today_date.month)[1]), datetime.time.max)
    elif period == "year":
        start_date = today_date.replace(month=1, day=1)
        end_date = datetime.datetime.combine(today_date.replace(month=12, day=31), datetime.time.max)
    else:
        return Response(
            {"error": "Periodo no válido, use 'week', 'month' o 'year'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    servicios = (
            ServicioRealizado.objects.active()
            .filter(fecha__range=[start_date, end_date])
            .values("servicio__nombre")
            .annotate(total_servicios=Count("servicio"))
            .order_by("-total_servicios")
        )
    
    if strLimit:
        servicios = servicios[:int(strLimit)]

    return Response(servicios, status=status.HTTP_200_OK)

@api_view(["GET"])
def performance_services_products(request: Request):
    strLimit = request.query_params.get("limit")
    
    top_servicios = Servicio.objects.active().annotate(num_realizados=Count('servicios_realizados')).order_by('-num_realizados')
    
    if strLimit:
        top_servicios = top_servicios[:int(strLimit)]
    
    data_servicios = []

    for servicio in top_servicios:
        num_realizados = servicio.num_realizados
        variacion_total = 0
        
        # Obtener los registros de ServicioRealizado para este servicio
        servicios_realizados = ServicioRealizado.objects.active().filter(servicio=servicio)
        
        for servicio_realizado in servicios_realizados:
            # Obtener los productos utilizados en cada ServicioRealizado
            productos_utilizados = ServicioRealizadoProducto.objects.active().filter(servicio_realizado=servicio_realizado)
            
            for producto_utilizado in productos_utilizados:
                #usos_estimados = producto_utilizado.producto.usos_est
                # Calcular la variación total en el uso de productos
                variacion_total += (producto_utilizado.cantidad - 1)
        
        data_servicios.append({
            'servicio': servicio.nombre,
            'num_realizados': num_realizados,
            'variacion_uso': variacion_total
        })
        
    return Response(data_servicios)