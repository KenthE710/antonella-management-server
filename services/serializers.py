from rest_framework import serializers

from core.mixin import ExcludeAbstractFieldsMixin
from inventory.serializers import ProductoOfServicioSerializer, ProductoSelectorSerializer
from staff.serializers import PersonalNamesSerializer
from customers.serializers import ClienteSerializer
from .models import (
    Servicio,
    ServicioEstado,
    ServicioRealizado,
    ServicioRealizadoProducto,
    ServicioImg,
)


class ServicioEstadoSimpleSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ServicioEstado
        fields = ["id", "nombre"]


class ServicioSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"

class ServicioViewSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    encargado = PersonalNamesSerializer()
    productos = ProductoOfServicioSerializer(many=True)
    estado = ServicioEstadoSimpleSerializer()
    disponibilidad = serializers.SerializerMethodField()
    
    class Meta:
        model = Servicio
        fields = "__all__"
        
    def get_disponibilidad(self, obj):
        return obj.get_disponibilidad


class ServicioGridSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    encargado = PersonalNamesSerializer()
    productos = ProductoSelectorSerializer(many=True)
    estado = ServicioEstadoSimpleSerializer()
    disponibilidad = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Servicio
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "tiempo_est",
            "encargado",
            "productos",
            "disponibilidad",
            "estado",
            "cover",
        ]

    def get_disponibilidad(self, obj):
        if hasattr(obj, "disponibilidad"):
            return obj.disponibilidad
        return None

    def get_cover(self, obj):
        if hasattr(obj, "cover") and len(obj.cover) > 0:
            url = obj.cover[0].imagen.url
            request = self.context.get("request", None)
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class ServicioSimpleSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = [
            "id",
            "nombre",
        ]


class ServicioRealizadoSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ServicioRealizado
        fields = "__all__"


class ServicioRealizadoProductoSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ServicioRealizadoProducto
        fields = "__all__"


class ServicioRealizadoProductoSimpleSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    producto = ProductoSelectorSerializer()

    class Meta:
        model = ServicioRealizadoProducto
        fields = ["id", "cantidad", "producto", "lote"]


class ServicioRealizadoAllSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    cliente = ClienteSerializer()
    servicio = ServicioSimpleSerializer()
    productos_utilizados = ServicioRealizadoProductoSimpleSerializer(many=True)

    class Meta:
        model = ServicioRealizado
        fields = "__all__"


class ServicioImgSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = ServicioImg
        fields = "__all__"

    def get_name(self, obj):
        return obj.name
