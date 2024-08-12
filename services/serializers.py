from rest_framework import serializers

from core.mixin import ExcludeAbstractFieldsMixin
from inventory.serializers import ProductoSelectorSerializer
from staff.serializers import PersonalNamesSerializer
from customers.serializers import ClienteSerializer
from .models import Servicio, ServicioRealizado, ServicioRealizadoProducto


class ServicioSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"


class ServicioGridSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    encargado = PersonalNamesSerializer()
    productos = ProductoSelectorSerializer(many=True)

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
            "status",
        ]


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
