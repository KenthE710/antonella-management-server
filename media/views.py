from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MediaFile
from .serializers import MediaFileSerializer


class MediaFileView(viewsets.ModelViewSet):
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    parser_classes = (MultiPartParser, FormParser)
