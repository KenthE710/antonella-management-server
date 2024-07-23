from django.urls import include, path
from rest_framework import routers
from .views import ClienteView

router = routers.DefaultRouter()
router.register(r"cliente", ClienteView, "cliente")

urlpatterns = [
    path("api/v1/", include(router.urls))
]
