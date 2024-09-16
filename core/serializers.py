from rest_framework import serializers

from .models import ServicioEspecialidad
from .mixin import ExcludeAbstractFieldsMixin

class PaginacionSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1)
    page_size = serializers.IntegerField(min_value=1)

class ServicioEspecialidadSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ServicioEspecialidad
        fields = "__all__"


class ServicioEspecialidadSimpleSerializer(
    ExcludeAbstractFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = ServicioEspecialidad
        fields = ["id", "nombre"]
