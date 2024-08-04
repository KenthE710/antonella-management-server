from django.urls import include, path
from rest_framework import routers
from .views import MediaFileView

router = routers.DefaultRouter()
router.register(r"media-file", MediaFileView, "media-file")

urlpatterns = [path("", include(router.urls))]
