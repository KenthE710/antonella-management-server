from django.urls import include, path
from rest_framework import routers
from users import views
from rest_framework_simplejwt.views import TokenRefreshView

# router = routers.DefaultRouter()
# router.register(r"user", views.UserView, "user")

urlpatterns = [
    # path("api/v1/", include(router.urls)),
    path("api/v1/login/", views.login),
    # path("signup/", views.signup),
    # path("test/", views.test_token),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/refresh/", views.refresh_token, name="token_refresh"),
]
