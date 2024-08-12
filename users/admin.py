from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if (
            not obj
        ):  # If obj is None, the user is not yet created, so don't show profile inline
            return []
        return super().get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


def superuser_check(user: AbstractUser) -> bool:
    return user.is_active and user.is_superuser


def user_is_staff(user: AbstractUser) -> bool:
    return user.is_active and user.is_staff


# admin.site.login = user_passes_test(user_is_staff)(admin.site.login)
