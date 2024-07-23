from rest_framework import serializers

from core.mixin import ExcludeAbstractFieldsMixin
from .models import Producto, ProductoImg, ProductoMarca, ProductoTipo, Lote


class ProductoSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"


class ProductoImgSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductoImg
        fields = "__all__"


class ProductoMarcaSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductoMarca
        fields = "__all__"


class ProductoTipoSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductoTipo
        fields = "__all__"


class LoteSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = "__all__"
