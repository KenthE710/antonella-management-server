from django.urls import include, path
from rest_framework import routers
from .views import ParametroView

router = routers.DefaultRouter()
router.register(r"parametro", ParametroView, "parametro")

urlpatterns = [
    path("api/v1/", include(router.urls))
]
