import calendar
import datetime
from decimal import Decimal
from dateutil import parser
from django.utils import timezone
from django.db.models import (
    Sum,
    Count,
    Q,
    Prefetch,
)
from django.db.models.manager import BaseManager
from rest_framework.request import Request
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import AllowAny

from .models import Producto, ProductoImg, ProductoMarca, ProductoTipo, Lote
from .serializers import (
    AssociateImgWithProductSerializer,
    LoteAllSerializer,
    LoteViewSerializer,
    ProductoAllSerializer,
    ProductoMarcaSelectorSerializer,
    ProductoSelectorSerializer,
    ProductoSerializer,
    ProductoImgSerializer,
    ProductoMarcaSerializer,
    ProductoTipoSelectorSerializer,
    ProductoTipoSerializer,
    LoteSerializer,
    ProductosMasUsadosSerializer,
    SimpleProductoImgSerializer,
)


@permission_classes([AllowAny])
class ProductoView(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(methods=["post"], detail=False)
    def get_by_ids(self, request: Request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response(
                {"msg": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        productos = Producto.objects.filter(id__in=ids)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))

        p_nombre = request.query_params.get("nombre")
        p_status = request.query_params.get("status")
        p_sku = request.query_params.get("sku")
        p_tipo = request.query_params.get("tipo")

        productos_queryset: BaseManager[Producto] = (
            Producto.objects.select_related("tipo", "marca")
            .prefetch_related(
                Prefetch(
                    "imgs",
                    queryset=ProductoImg.objects.filter(is_cover=True)
                    .only("producto", "url_imagen_externa", "imagen")
                    .active(),
                    to_attr="covers",
                )
            )
            # .only("tipo__nombre", "marca__nombre" "nombre", "sku", "created_at")
            .with_posee_existencias()
            .active()
        )

        if p_nombre:
            productos_queryset = productos_queryset.filter(nombre__icontains=p_nombre)
        if p_sku:
            productos_queryset = productos_queryset.filter(sku__icontains=p_sku)
        if p_status:
            productos_queryset = productos_queryset.filter(
                posee_existencias=p_status == "true"
            )
        if p_tipo:
            productos_queryset = productos_queryset.filter(
                tipo__nombre__icontains=p_tipo
            )

        if not hasOffset:
            data = [
                {
                    "id": prod.id,
                    "tipo": prod.tipo.nombre,
                    "marca": prod.marca.nombre,
                    "nombre": prod.nombre,
                    "sku": prod.sku,
                    "precio": prod.precio,
                    "usos_est": prod.usos_est,
                    "status": 1 if prod.posee_existencias else 0,
                    "cover": prod.covers[0].url if len(prod.covers) > 0 else "",
                }
                for prod in productos_queryset
            ]

            return Response(
                {"count": len(data), "next": None, "previous": None, "results": data},
                status=status.HTTP_200_OK,
            )

        page = self.paginate_queryset(productos_queryset)
        if page is not None:
            data = [
                {
                    "id": prod.id,
                    "tipo": prod.tipo.nombre,
                    "marca": prod.marca.nombre,
                    "nombre": prod.nombre,
                    "sku": prod.sku,
                    "precio": prod.precio,
                    "usos_est": prod.usos_est,
                    "status": 1 if prod.posee_existencias else 0,
                    "cover": request.build_absolute_uri(prod.covers[0].url) if len(prod.covers) > 0 else "",
                }
                for prod in page
            ]

            if isinstance(self.paginator, LimitOffsetPagination):
                offset = int(self.paginator.get_offset(request))

                for i, item in enumerate(data):
                    item["row_number"] = int(offset) + (i + 1)

            return self.get_paginated_response(data)

        return Response(
            {"msg": "No se pudo paginar el resultado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(methods=["get"], detail=False)
    def selector(self, request: Request):
        queryset = Producto.objects.only("id", "nombre", "sku").active().all()
        serializer = ProductoSelectorSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=True)
    def view(self, request: Request, pk=None):
        producto: Producto = self.get_object()
        serializer = ProductoAllSerializer(producto)
        return Response(serializer.data)

    @action(methods=["get", "post"], detail=True)
    def img(self, request: Request, pk=None):
        if request.method == "GET":
            return self.list_img()
        elif request.method == "POST":
            return self.upload_img(request)

    def list_img(self):
        producto: Producto = self.get_object()
        producto_img_queryset: BaseManager[ProductoImg] = producto.imgs.active().all()
        serializer = SimpleProductoImgSerializer(
            producto_img_queryset, many=True, context=self.get_serializer_context()
        )

        producto_img = [
            {
                "id": img["id"],
                "is_cover": img["is_cover"],
                "url": img["imagen"] if img["imagen"] else img["url_imagen_externa"],
                "name": img["name"],
            }
            for img in serializer.data
        ]

        return Response(producto_img, status=status.HTTP_200_OK)

    def upload_img(self, request: Request):
        producto: Producto = self.get_object()

        request.data.update({"producto": producto.id})
        serializer = ProductoImgSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        img = serializer.save()

        return Response(
            {
                "id": img.id,
                "is_cover": img.is_cover,
                "url": img.url,
                "name": img.name,
            },
            status=status.HTTP_201_CREATED,
            headers={"Location": "url"},
        )

    @action(methods=["get"], detail=False)
    def search(self, request: Request):
        query = request.query_params.get("q", "")
        queryset = self.get_queryset().filter(
            Q(nombre__icontains=query) | Q(sku__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductoImgView(viewsets.ModelViewSet):
    queryset = ProductoImg.objects.all()
    serializer_class = ProductoImgSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        img = serializer.instance
        return Response(
            {
                "id": img.id,
                "is_cover": img.is_cover,
                "url": img.url,
                "name": img.name,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(methods=["post"], detail=False, url_path="associate-with-product")
    def associate_with_product(self, request: Request):
        serializer = AssociateImgWithProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        imgs_id: list[int] = serializer.validated_data.get("imgs_id", [])
        producto_id: int | None = serializer.validated_data.get("producto_id")

        if len(imgs_id) == 0 or producto_id is None:
            return Response(
                {"msg": "No se encontraron los parámetros requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        imgs: BaseManager[ProductoImg] = (
            ProductoImg.objects.filter(id__in=imgs_id).active().all()
        )
        producto = Producto.objects.get(id=producto_id)

        for img in imgs:
            img.producto = producto
            img.is_temp = False
            img.save()

        return Response(
            {"msg": "Imagenes asociadas con éxito"},
            status=status.HTTP_200_OK,
        )


class ProductoMarcaView(viewsets.ModelViewSet):
    queryset = ProductoMarca.objects.active().all()
    serializer_class = ProductoMarcaSerializer

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        queryset = self.filter_queryset(self.get_queryset())

        strNombre = request.query_params.get("nombre")

        if strNombre:
            queryset = queryset.filter(nombre__icontains=strNombre)

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
    def selector(self, request: Request):
        queryset = ProductoMarca.objects.only("id", "nombre").active().all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductoMarcaSelectorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductoMarcaSelectorSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductoTipoView(viewsets.ModelViewSet):
    queryset = ProductoTipo.objects.active().all()
    serializer_class = ProductoTipoSerializer

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        queryset = self.filter_queryset(self.get_queryset())

        strNombre = request.query_params.get("nombre")
        strDescripcion = request.query_params.get("descripcion")

        if strNombre:
            queryset = queryset.filter(nombre__icontains=strNombre)
        if strDescripcion:
            queryset = queryset.filter(descripcion__icontains=strDescripcion)

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
    def selector(self, request: Request):
        queryset = ProductoTipo.objects.only("id", "nombre").active().all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductoTipoSelectorSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductoTipoSelectorSerializer(queryset, many=True)
        return Response(serializer.data)


class LoteView(viewsets.ModelViewSet):
    queryset = Lote.objects.active().all()
    serializer_class = LoteSerializer

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        hasOffset = bool(request.query_params.get("offset"))
        # Filters Params
        strFeCompraInicio = request.query_params.get("fe_compra_inicio")
        strFeCompraFin = request.query_params.get("fe_compra_fin")
        strFeExpInicio = request.query_params.get("fe_exp_inicio")
        strFeExpFin = request.query_params.get("fe_exp_fin")
        strProducto = request.query_params.get("producto")
        strCant = request.query_params.get("cant")
        strCosto = request.query_params.get("costo")
        strStates = request.query_params.get("state")

        queryset = self.filter_queryset(self.get_queryset())

        if strFeCompraInicio and strFeCompraFin:
            DateFeCompraInicio = parser.isoparse(strFeCompraInicio)
            DateFeCompraFin = parser.isoparse(strFeCompraFin)

            queryset = queryset.filter(
                fe_compra__range=[DateFeCompraInicio, DateFeCompraFin]
            )

        if strFeExpInicio and strFeExpFin:
            DateFeExpInicio = parser.isoparse(strFeExpInicio)
            DateFeExpFin = parser.isoparse(strFeExpFin)

            queryset = queryset.filter(fe_exp__range=[DateFeExpInicio, DateFeExpFin])

        if strProducto:
            queryset = queryset.filter(
                Q(producto__nombre__icontains=strProducto)
                | Q(producto__sku__icontains=strProducto)
            )

        if strCant:
            queryset = queryset.filter(cant=int(strCant))

        if strCosto:
            queryset = queryset.filter(costo=Decimal(strCosto))

        if strStates:
            arrayStatesfilters = []

            for strState in strStates.split(","):
                if strState == "0":
                    arrayStatesfilters.append(
                        Q(
                            servicios_restantes__gt=0,
                            retirado=False,
                            fe_exp__gt=timezone.now(),
                        )
                    )
                elif strState == "1":
                    arrayStatesfilters.append(Q(servicios_restantes=0))
                elif strState == "2":
                    arrayStatesfilters.append(Q(retirado=True))
                elif strState == "3":
                    arrayStatesfilters.append(
                        Q(retirado=False, fe_exp__lte=timezone.now())
                    )

            combined_condition = Q()
            for condition in arrayStatesfilters:
                combined_condition |= condition

            queryset = queryset.with_servicios_restantes().filter(combined_condition)

        page = self.paginate_queryset(queryset)
        if (page is not None) and hasOffset:
            serializer = LoteAllSerializer(page, many=True)
            data = serializer.data

            if isinstance(self.paginator, LimitOffsetPagination):
                offset = int(self.paginator.get_offset(request))

                for i, item in enumerate(data):
                    item["row_number"] = int(offset) + (i + 1)

            return self.get_paginated_response(data)

        serializer = LoteAllSerializer(queryset, many=True)
        return Response({"count": len(serializer.data), "results": serializer.data})

    @action(methods=["get"], detail=True)
    def view(self, request: Request, pk=None):
        lote: Lote = self.get_object()
        serializer = LoteViewSerializer(lote)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        motivo = self.request.query_params.get("motivo", "")
        instance.motivo = motivo
        instance.save()
        instance.delete()

class StatisticsViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(detail=False, methods=["get"])
    def total_productos_por_tipo(self, request):
        """
        Retorna el total de productos por tipo.
        """
        CountbyType = Producto.objects.values("tipo__nombre").annotate(
            total=Count("id")
        )
        return Response(
            [
                {"tipo": data["tipo__nombre"], "total": data["total"]}
                for data in CountbyType
            ],
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def productos_por_marca(self, request):
        """
        Retorna el total de productos por marca.
        """
        CountbyMarca = Producto.objects.active().values("marca__nombre").annotate(
            total=Count("id")
        )
        return Response(
            [
                {"marca": data["marca__nombre"], "total": data["total"]}
                for data in CountbyMarca
            ],
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def valor_inventario(self, request):
        """
        Retorna el valor total del inventario.
        """
        data = {
            "total": 0, 
            "semanal": { "actual": 0, "anterior": 0}, 
            "mensual": { "actual": 0, "anterior": 0}, 
            "anual": { "actual": 0, "anterior": 0}
        }
        
        total_data = Lote.objects.active().aggregate(total=Sum("costo"))
        if total_data is not None and total_data["total"] is not None:
            data['total'] = total_data["total"]
        
        today = timezone.now()
        today_date = today.date()

        # Week data
        start_current_week = today_date - datetime.timedelta(days=today_date.weekday())
        end_current_week = datetime.datetime.combine(start_current_week + datetime.timedelta(days=6), datetime.time.max)
        start_last_week = start_current_week - datetime.timedelta(days=7)
        end_last_week = datetime.datetime.combine(start_last_week + datetime.timedelta(days=6), datetime.time.max)

        current_week_data = Lote.objects.active().filter(fe_compra__range=[start_current_week, end_current_week]).aggregate(total=Sum("costo"))
        last_week_data = Lote.objects.active().filter(fe_compra__range=[start_last_week, end_last_week]).aggregate(total=Sum("costo"))
        
        if current_week_data is not None and current_week_data["total"] is not None:
            data['semanal']['actual'] = current_week_data["total"]
        if last_week_data is not None and last_week_data["total"] is not None:
            data['semanal']['anterior'] = last_week_data["total"]

        # Month data
        start_current_month = today_date.replace(day=1)
        end_current_month = datetime.datetime.combine(today_date.replace(day=calendar.monthrange(today_date.year, today_date.month)[1]), datetime.time.max)
        start_last_month = start_current_month - datetime.timedelta(days=calendar.monthrange(today_date.year, today_date.month - 1)[1])
        end_last_month = datetime.datetime.combine(start_last_month.replace(day=calendar.monthrange(today_date.year, today_date.month - 1)[1]), datetime.time.max)
        
        current_month_data = Lote.objects.active().filter(fe_compra__range=[start_current_month, end_current_month]).aggregate(total=Sum("costo"))
        last_month_data = Lote.objects.active().filter(fe_compra__range=[start_last_month, end_last_month]).aggregate(total=Sum("costo"))

        if current_month_data is not None and current_month_data["total"] is not None:
            data['mensual']['actual'] = current_month_data["total"]
        if last_month_data is not None and last_month_data["total"] is not None:
            data['mensual']['anterior'] = last_month_data["total"]

        # Year data
        start_current_year = today_date.replace(month=1, day=1)
        end_current_year = datetime.datetime.combine(today_date.replace(month=12, day=31), datetime.time.max)
        start_last_year = start_current_year.replace(year=today_date.year - 1)
        end_last_year = datetime.datetime.combine(today_date.replace(year=today_date.year - 1, month=12, day=31), datetime.time.max)
        
        current_year_data = Lote.objects.active().filter(fe_compra__range=[start_current_year, end_current_year]).aggregate(total=Sum("costo"))
        last_year_data = Lote.objects.active().filter(fe_compra__range=[start_last_year, end_last_year]).aggregate(total=Sum("costo"))
        
        if current_year_data is not None and current_year_data["total"] is not None:
            data['anual']['actual'] = current_year_data["total"]
        if last_year_data is not None and last_year_data["total"] is not None:
            data['anual']['anterior'] = last_year_data["total"]
        
        return Response(data)

    @action(detail=False, methods=["get"])
    def cantidad_usos_estimados(self, request):
        """
        Retorna la cantidad total de usos estimados de todos los productos.
        """
        data = Producto.objects.aggregate(total=Sum("usos_est"))
        return Response(data)

    @action(detail=False, methods=["get"])
    def productos_mas_utilizados(self, request):
        from services.models import ServicioRealizadoProducto
        """
        Retorna una lista de los productos más utilizados (ordenados por usos).
        """
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
            
        productos_usados = (
                ServicioRealizadoProducto.objects.active().filter(servicio_realizado__fecha__range=[start_date, end_date])
                .values("producto__id", "producto__nombre", "producto__sku")
                .annotate(usos=Sum("cantidad"))
                .order_by("-usos")
            )

        if strLimit:
            productos_usados = productos_usados[:int(strLimit)]
        
        serializer = ProductosMasUsadosSerializer(productos_usados, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def lotes_cerca_de_expirar(self, request):
        """
        Retorna una lista de los lotes que están cerca de expirar.
        """
        umbral_dias = int(request.query_params.get('umbral', 10))
        fecha_actual = timezone.now()
        fecha_limite = fecha_actual + datetime.timedelta(days=umbral_dias)
        
        data = Lote.objects.active().filter(retirado=False, fe_exp__range=[fecha_actual, fecha_limite]).order_by("fe_exp")
        serializer = LoteAllSerializer(data, many=True)
        return Response(serializer.data)