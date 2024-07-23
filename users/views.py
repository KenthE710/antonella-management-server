from datetime import datetime
import pytz
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

from django.contrib.auth.models import User


def superuser_check(user: User) -> bool:
    return user.is_active and user.is_superuser


# Create your views here.
class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = get_object_or_404(User, username=username)

    if not user.check_password(password):
        return Response(
            {"msg": "contraseña no valida"},
            status=status.HTTP_200_OK,
        )

    token, created = Token.objects.get_or_create(user=user)
    return Response(
        {
            "msg": "ok",
            "user": {
                "token": token.key,
                "id": user.id, # type: ignore
                "name": user.username,
                "email": user.email,
                "time": datetime.now(pytz.timezone("America/Guayaquil")).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            },
        },
        status=status.HTTP_200_OK,
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
