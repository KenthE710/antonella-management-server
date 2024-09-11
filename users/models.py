from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Modelo que representa el perfil de usuario.
    Atributos:
    - user: Campo de relación uno a uno con el modelo User.
    - avatar: Campo de imagen que almacena el avatar del usuario.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
