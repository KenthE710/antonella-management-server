from rest_framework import serializers

from core.serializers import ServicioEspecialidadSimpleSerializer

from .models import Personal, PersonalState
from core.mixin import ExcludeAbstractFieldsMixin

class PersonalStateSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = PersonalState
        fields = '__all__'

class PersonalSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = '__all__'
        
class PersonalFullSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    estado = PersonalStateSerializer()
    especialidades = ServicioEspecialidadSimpleSerializer(many=True)
    class Meta:
        model = Personal
        fields = '__all__'
        
class PersonalNamesSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = ['id', 'nombre', 'apellido']