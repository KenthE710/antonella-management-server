from rest_framework import serializers

from core.mixin import ExcludeAbstractFieldsMixin
from .models import Producto, ProductoImg, ProductoMarca, ProductoTipo, Lote


class ProductoImgSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductoImg
        fields = "__all__"


class AssociateImgWithProductSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    imgs_id = serializers.ListField(child=serializers.IntegerField())


class SimpleProductoImgSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ProductoImg
        fields = ["id", "is_cover", "imagen", "url_imagen_externa", "name"]


class ProductoMarcaSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductoMarca
        fields = "__all__"


class ProductoMarcaSelectorSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ProductoMarca
        fields = ["id", "nombre"]


class ProductoTipoSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductoTipo
        fields = "__all__"


class ProductoTipoSelectorSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ProductoTipo
        fields = ["id", "nombre"]


class LoteSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Lote
        fields = "__all__"


class ProductoSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"


class ProductoAllSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    tipo = ProductoTipoSerializer()
    marca = ProductoMarcaSerializer()

    class Meta:
        model = Producto
        fields = [
            "id",
            "tipo",
            "marca",
            "nombre",
            "sku",
            "precio",
            "usos_est",
            "posee_existencias",
            "existencias",
            "usos_restantes",
        ]


class ProductoSelectorSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = Producto
        fields = ["id", "nombre", "sku"]


class LoteAllSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    producto = ProductoSelectorSerializer()

    class Meta:
        model = Lote
        fields = [
            "id",
            "producto",
            "fe_compra",
            "fe_exp",
            "cant",
            "costo",
            "consumido",
            "retirado",
            "state",
        ]

class LoteViewSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    producto = ProductoSelectorSerializer()

    class Meta:
        model = Lote
        fields = [
            "id",
            "producto",
            "fe_compra",
            "fe_exp",
            "cant",
            "costo",
            "consumido",
            "retirado",
            "state",
            "servicios_Realizados",
            "servicios_restantes",
        ]
