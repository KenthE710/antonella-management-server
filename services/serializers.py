from rest_framework import serializers

from inventory.serializers import ProductoSelectorSerializer
from staff.serializers import PersonalNamesSerializer
from .models import Servicio

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'
        
class ServicioGridSerializer(serializers.ModelSerializer):
    encargado = PersonalNamesSerializer()
    productos = ProductoSelectorSerializer()
    class Meta:
        model = Servicio
        fields = '__all__'