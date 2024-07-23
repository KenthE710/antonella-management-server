from django.urls import include, path
from rest_framework import routers
from .views import MediaFileView

router = routers.DefaultRouter()
router.register(r"", MediaFileView, "media-file")

urlpatterns = [path("api/v1/", include(router.urls))]
