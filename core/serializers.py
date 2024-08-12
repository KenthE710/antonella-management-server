from rest_framework import serializers
from .models import Test
from .mixin import ExcludeAbstractFieldsMixin

class PaginacionSerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1)
    page_size = serializers.IntegerField(min_value=1)

class TestSerializer(ExcludeAbstractFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = "__all__"
