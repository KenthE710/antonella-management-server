from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r"servicio", views.ServicioView, "servicio")
router.register(
    r"servicio_realizado", views.ServicioRealizadoView, "servicio_realizado"
)
router.register(
    r"servicio_realizado_producto",
    views.ServicioRealizadoProductoView,
    "servicio_realizado_producto",
)
router.register(
    r'servicio_img',
    views.ServicioImgView,
    'servicio_img'
)

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path(
        "api/v1/stats/servicios-realizados/",
        views.service_per_months,
        name="servicios-realizados",
    ),
    path(
        "api/v1/stats/most-performed-services/",
        views.most_performed_services,
        name="most-performed-services",
    ),
    path(
        "api/v1/stats/performance-services-products/",
        views.performance_services_products,
        name="performance-services-products",
    ),
]
