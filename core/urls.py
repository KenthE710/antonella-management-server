from django.urls import include, path
from rest_framework import routers
from .views import TestView

router = routers.DefaultRouter()
router.register(r"test", TestView, "test")

urlpatterns = [
    #path("", include(router.urls))
]
