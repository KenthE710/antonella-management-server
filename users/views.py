from datetime import datetime, timedelta
import pytz
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

from django.contrib.auth.models import User


def superuser_check(user: User) -> bool:
    return user.is_active and user.is_superuser


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = get_object_or_404(User, username=username)

    if not user.check_password(password):
        return Response(
            {"msg": "contraseña no valida"},
            status=status.HTTP_200_OK,
        )

    # Generar tokens de acceso y refresh
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    userSerializer = UserSerializer(user, context={"request": request})

    return Response(
        {
            "msg": "ok",
            "user": {
                "access_token": str(access_token),
                "refresh_token": str(refresh),
                "id": userSerializer.data.get("id"),
                "name": userSerializer.data.get("username"),
                "email": userSerializer.data.get("email"),
                "time": datetime.now(pytz.timezone("America/Guayaquil")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                # "expired": datetime.now(pytz.timezone("America/Guayaquil")) + timedelta(minutes=5),
                "expired": datetime.now(pytz.timezone("America/Guayaquil"))
                + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                "avatar": (
                    userSerializer.data.get("profile").get("avatar", "")
                    if userSerializer.data.get("profile")
                    else ""
                ),
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def refresh_token(request):
    refresh_token_str = request.data.get("refresh")

    try:
        # Validar el refresh token
        refresh = RefreshToken(refresh_token_str)
        new_access_token = refresh.access_token

        # Obtener el usuario a partir del token
        user = User.objects.get(id=refresh["user_id"])
        userSerializer = UserSerializer(user, context={"request": request})

        return Response(
            {
                "msg": "ok",
                "user": {
                    "access_token": str(new_access_token),
                    "refresh_token": str(refresh),
                    "id": userSerializer.data.get("id"),
                    "name": userSerializer.data.get("username"),
                    "email": userSerializer.data.get("email"),
                    "time": datetime.now(pytz.timezone("America/Guayaquil")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "expired": datetime.now(pytz.timezone("America/Guayaquil"))
                    + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
                    "avatar": (
                        userSerializer.data.get("profile").get("avatar", "")
                        if userSerializer.data.get("profile")
                        else ""
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )

    except (TokenError, InvalidToken) as e:
        return Response(
            {"msg": "Refresh token inválido o expirado"},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["POST"])
def signup(request):
    userSerializer = UserSerializer(data=request.data)

    if userSerializer.is_valid():
        user = userSerializer.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {"msg": "ok", "token": token.key, "user": userSerializer.data},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(userSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(
        {"msg": "request by {}".format(request.user.email)}, status=status.HTTP_200_OK
    )
