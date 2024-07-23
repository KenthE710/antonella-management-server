from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.decorators import user_passes_test

# Register your models here.
# admin.site.register(User)


def superuser_check(user: AbstractUser) -> bool:
    return user.is_active and user.is_superuser

def user_is_staff(user: AbstractUser) -> bool:
    return user.is_active and user.is_staff

#admin.site.login = user_passes_test(user_is_staff)(admin.site.login)