from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка панели администратора для модели 'User'."""
    add_fieldsets = (
        ('Регистрация пользователя', {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name',
                'email', 'password1', 'password2',
            ),
        }),
    )
    list_filter = UserAdmin.list_filter + ('username', 'email',)
