from rest_framework import serializers

from core.mixin import ExcludeAbstractFieldsMixin
from .models import Cliente

class ClienteSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"
