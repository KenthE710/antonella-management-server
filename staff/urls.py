from django.urls import include, path
from rest_framework import routers
from .views import PersonalView

router = routers.DefaultRouter()
router.register(r"personal", PersonalView, "personal")

urlpatterns = [
    path("api/v1/", include(router.urls))
]
