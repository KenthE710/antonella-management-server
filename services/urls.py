from django.urls import include, path
from rest_framework import routers
from .views import ServicioView

router = routers.DefaultRouter()
router.register(r"servicio", ServicioView, "servicio")

urlpatterns = [
    path("api/v1/", include(router.urls))
]
