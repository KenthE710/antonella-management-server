from django.urls import include, path
from rest_framework import routers
from .views import ServicioView, ServicioRealizadoView, ServicioRealizadoProductoView

router = routers.DefaultRouter()
router.register(r"servicio", ServicioView, "servicio")
router.register(r"servicio_realizado", ServicioRealizadoView, "servicio_realizado")
router.register(r"servicio_realizado_producto", ServicioRealizadoProductoView, "servicio_realizado_producto")

urlpatterns = [
    path("api/v1/", include(router.urls))
]
