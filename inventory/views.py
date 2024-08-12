from rest_framework.request import Request
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models.manager import BaseManager
from django.db.models import Sum, Count
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated

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
    SimpleProductoImgSerializer,
)


class ProductoView(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(methods=["post"], detail=False)
    def get_by_ids(self, request: Request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"msg": "No IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        productos = Producto.objects.filter(id__in=ids)
        serializer = self.get_serializer(productos, many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        nombre = request.query_params.get("nombre")
        status = request.query_params.get("status")
        sku = request.query_params.get("sku")
        
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
            .active()
        )
        
        if nombre:
            productos_queryset = productos_queryset.filter(nombre__icontains=nombre)
        if sku:
            productos_queryset = productos_queryset.filter(sku__icontains=sku)
        if status:
            productos_queryset = productos_queryset.filter(posee_existencias=status != 1)

        page = self.paginate_queryset(productos_queryset)
        if page is not None:
            return self.get_paginated_response(
                [
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
                    for prod in page
                ]
            )

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
        serializer = SimpleProductoImgSerializer(producto_img_queryset, many=True, context=self.get_serializer_context())

        producto_img = [
            {
                "id": img['id'],
                "is_cover": img['is_cover'],
                "url":  img['imagen'] if img['imagen'] else img['url_imagen_externa'],
                "name": img['name'],
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
            Q(nombre__icontains=query)
            | Q(sku__icontains=query)
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
        return self.list(request)

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
        return self.list(request)

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
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LoteAllSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = LoteAllSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(methods=["get"], detail=True)
    def view(self, request: Request, pk=None):
        lote: Lote = self.get_object()
        serializer = LoteViewSerializer(lote)
        return Response(serializer.data)



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
        CountbyMarca = Producto.objects.values("marca__nombre").annotate(
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
        data = Lote.objects.aggregate(valor_total=Sum("costo"))
        if data is None or data["valor_total"] is None:
            return Response({"valor_total": 0})
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
        """
        Retorna una lista de los productos más utilizados (ordenados por usos estimados).
        """
        data = Producto.objects.all().order_by("-usos_est")[:10]
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)
