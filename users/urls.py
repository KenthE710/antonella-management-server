from django.urls import include, path
from rest_framework import routers
from users import views

router = routers.DefaultRouter()
router.register(r"user", views.UserView, "user")

urlpatterns = [
    #path("api/v1/", include(router.urls)),
    path("login/", views.login),
    #path("signup/", views.signup),
    #path("test/", views.test_token),
]
