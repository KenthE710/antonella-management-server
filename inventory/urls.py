from django.urls import include, path
from rest_framework import routers
from .views import (
    ProductoView,
    ProductoImgView,
    ProductoMarcaView,
    ProductoTipoView,
    LoteView,
    StatisticsViewSet,
)

router = routers.DefaultRouter()
router.register(r"producto", ProductoView, "producto")
router.register(r"producto_img", ProductoImgView, "producto_img")
router.register(r"producto_marca", ProductoMarcaView, "producto_marca")
router.register(r"producto_tipo", ProductoTipoView, "producto_tipo")
router.register(r"lote", LoteView, "lote")
router.register(r"stats", StatisticsViewSet, "stats")

urlpatterns = [path("api/v1/", include(router.urls))]
