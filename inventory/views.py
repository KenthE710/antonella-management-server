from rest_framework.request import Request
from django.core.paginator import Paginator
from django.db.models import Prefetch, QuerySet
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django.db.models.manager import BaseManager

from core.responses import ValidationErrorResponse
from core.serializers import PaginacionSerializer
from core.pagination import createdDateCursorPagination
from .models import Producto, ProductoImg, ProductoMarca, ProductoTipo, Lote
from .serializers import (
    ProductoSerializer,
    ProductoImgSerializer,
    ProductoMarcaSerializer,
    ProductoTipoSerializer,
    LoteSerializer,
)


class ProductoView(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    @action(methods=["get"], detail=False)
    def get_productos_grid_cursor(self, request: Request):
        productos_json = []
        paginator = createdDateCursorPagination()

        productos_queryset = (
            Producto.objects.select_related("tipo")
            .only("tipo__nombre", "nombre", "sku", "created_date")
            .prefetch_related(
                Prefetch(
                    "imgs",
                    queryset=ProductoImg.objects.filter(is_cover=True).only(
                        "producto", "url"
                    )[:1],
                    to_attr="cover",
                )
            )
            .all()
        )

        productos: list[Producto] | None = paginator.paginate_queryset(
            productos_queryset, request
        )
        if productos is None:
            return Response(
                data={"msg": "No se encontraron datos"},
                status=status.HTTP_204_NO_CONTENT,
            )

        for prod in productos:
            productos_json.append(
                {
                    "id": prod.__getattribute__("id"),
                    "nombre": prod.nombre,
                    "tipo": prod.tipo.nombre,
                    "sku": prod.sku,
                    "cover": prod.__getattribute__("cover")[0].url,
                }
            )
        return paginator.get_paginated_response(productos_json)

    @action(methods=["get"], detail=False)
    def grid(self, request: Request):
        paginacionSerializer = PaginacionSerializer(data=request.query_params)
        paginacionSerializer.is_valid(raise_exception=True)

        productos_json = []
        page: int = paginacionSerializer.validated_data.get("page", 1)
        page_size: int = paginacionSerializer.validated_data.get("page_size", 10)

        productos_queryset: BaseManager[Producto] = (
            Producto.objects.select_related("tipo")
            .prefetch_related(
                Prefetch(
                    "imgs",
                    queryset=ProductoImg.objects.filter(is_cover=True).only(
                        "producto", "url_imagen_externa"
                    )[:1],
                    to_attr="cover",
                )
            )
            .only("tipo__nombre", "nombre", "sku", "created_at")
            .active()
            .all()
        )
        paginator = Paginator(productos_queryset, page_size)
        productos_page = paginator.get_page(page)
        productos: QuerySet[Producto] = productos_page.object_list

        for prod in productos:
            productos_json.append(
                {
                    "id": prod.id,
                    "tipo": {"id": prod.tipo.id, "nombre": prod.tipo.nombre},
                    "marca": {"id": prod.marca.id, "nombre": prod.marca.nombre},
                    "nombre": prod.nombre,
                    "sku": prod.sku,
                    "precio": prod.precio,
                    "usos_est": prod.usos_est,
                    "cover": prod.cover and prod.cover[0].url_imagen_externa or "",
                }
            )

        return Response(
            {
                "total": Producto.objects.active().count(),
                "list": productos_json,
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["post", "delete"], detail=True)
    def delete_producto(self, request: Request, pk=None):
        producto: Producto = self.get_object()
        producto.is_deleted = True
        producto.save()
        return Response(
            data={"msg": "Producto eliminado correctamente"},
            status=status.HTTP_200_OK,
        )

    @action(methods=["put"], detail=True)
    def update_producto(self, request: Request, pk=None):
        producto: Producto = self.get_object()
        serializer = self.get_serializer(producto, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Producto actualizado correctamente"}, status=status.HTTP_200_OK
            )

        return ValidationErrorResponse(
            serializer.errors, msg="Error en actualizar el producto"
        )

    @action(methods=["post"], detail=False)
    def create_producto(self, request: Request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"msg": "Producto creado correctamente"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductoImgView(viewsets.ModelViewSet):
    queryset = ProductoImg.objects.all()
    serializer_class = ProductoImgSerializer


class ProductoMarcaView(viewsets.ModelViewSet):
    queryset = ProductoMarca.objects.all()
    serializer_class = ProductoMarcaSerializer

    @action(methods=["get"], detail=False)
    def selector(self, request: Request):
        queryset = ProductoMarca.objects.values("id", "nombre")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductoTipoView(viewsets.ModelViewSet):
    queryset = ProductoTipo.objects.all()
    serializer_class = ProductoTipoSerializer
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        queryset = ProductoTipo.objects.values("id", "nombre", "descripcion")
        return Response(
            {"total": ProductoTipo.objects.count(), "list": queryset},
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False)
    def get_producto_tipo_selector(self, request: Request):
        queryset = ProductoTipo.objects.values("id", "nombre")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LoteView(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer
