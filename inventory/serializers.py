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
        
    def validate(self, data, **kwargs):
        force_save = self.context.get('force_save', False)
        
        if force_save:
            return data
        
        lote = self.instance if self.instance else Lote(**data)
        producto = lote.producto

        # Obtener la cantidad anterior si el lote ya existe
        if self.instance:  # Si el lote ya existe en la base de datos
            cantidad_anterior = self.instance.cant
        else:
            cantidad_anterior = 0  # Si es nuevo, la cantidad anterior es 0

        # Realizar las validaciones de existencias
        if producto.maximo is not None and producto.minimo is not None:
            existencias_actuales = producto.get_existencias or 0
            existencias = existencias_actuales - int(cantidad_anterior) + int(data['cant'])
            
            if existencias < producto.minimo:
                raise serializers.ValidationError(
                    f"Existencias menores al mínimo, mínimo: {producto.minimo}, existencias: {existencias_actuales}"
                )
            elif existencias > producto.maximo:
                raise serializers.ValidationError(
                    f"Existencias mayores al máximo permitido, máximo: {producto.maximo}, existencias: {existencias_actuales}"
                )
        
        return data

class ProductoSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = "__all__"

class ProductoWithExistenciasSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    existencias = serializers.SerializerMethodField()
    class Meta:
        model = Producto
        fields = "__all__"
        
    def get_existencias(self, obj):
        return obj.existencias

class ProductoAllSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    tipo = ProductoTipoSerializer()
    marca = ProductoMarcaSerializer()
    posee_existencias = serializers.SerializerMethodField()
    existencias = serializers.SerializerMethodField()
    usos_restantes = serializers.SerializerMethodField()

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
            "maximo",
            "minimo",
            "posee_existencias",
            "existencias",
            "usos_restantes",
        ]

    def get_posee_existencias(self, obj):
        return obj.get_posee_existencias
    
    def get_existencias(self, obj):
        return obj.get_existencias
    
    def get_usos_restantes(self, obj):
        return obj.get_usos_restantes

class ProductoSelectorSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = Producto
        fields = ["id", "nombre", "sku"]
        
class ProductoOfServicioSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    existencias = serializers.SerializerMethodField()
    class Meta:
        model = Producto
        fields = ["id", "nombre", "sku", "existencias"]

    def get_existencias(self, obj):
        return obj.get_existencias

class ProductosServicioGridSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    usos_restantes = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ["id", "nombre", "sku", "usos_restantes"]
        
    def get_usos_restantes(self, obj):
        return obj.get_usos_restantes

class LoteAllSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    producto = ProductoSelectorSerializer()
    consumido = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Lote
        fields = [
            "id",
            "producto",
            "fe_compra",
            "fe_exp",
            "cant",
            "costo",
            "motivo",
            "consumido",
            "retirado",
            "state",
        ]
        
    def get_consumido(self, obj):
        return obj.get_consumido

    def get_state(self, obj):
        return obj.get_state

class LoteViewSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    producto = ProductoSelectorSerializer()
    consumido = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    servicios_Realizados = serializers.SerializerMethodField()
    servicios_restantes = serializers.SerializerMethodField()

    class Meta:
        model = Lote
        fields = [
            "id",
            "producto",
            "fe_compra",
            "fe_exp",
            "cant",
            "costo",
            "motivo",
            "consumido",
            "retirado",
            "state",
            "servicios_Realizados",
            "servicios_restantes",
        ]
        
    def get_consumido(self, obj):
        return obj.get_consumido
    
    def get_state(self, obj):
        return obj.get_state

    def get_servicios_Realizados(self, obj):
        return obj.get_servicios_Realizados
    
    def get_servicios_restantes(self, obj):
        return obj.get_servicios_restantes
    
class ProductosMasUsadosSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='producto__id')
    nombre = serializers.CharField(source='producto__nombre')
    sku = serializers.CharField(source='producto__sku')
    usos = serializers.IntegerField()