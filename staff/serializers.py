from rest_framework import serializers
from .models import Personal
from core.mixin import ExcludeAbstractFieldsMixin

class PersonalSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = '__all__'
        
class PersonalNamesSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Personal
        fields = ['id', 'nombre', 'apellido']