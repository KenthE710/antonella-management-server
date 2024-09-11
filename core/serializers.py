from rest_framework import serializers
from .mixin import ExcludeAbstractFieldsMixin

class PaginacionSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1)
    page_size = serializers.IntegerField(min_value=1)
