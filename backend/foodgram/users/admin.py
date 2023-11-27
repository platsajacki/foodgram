from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow, ShoppingCard, FavouriteRecipe


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'Follow'."""
    list_display = (
        'user', 'following', 'date_added',
    )
    list_filter = (
        'user', 'following',
    )


@admin.register(FavouriteRecipe)
class FavouriteRecipeAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'FavouriteRecipe'."""
    list_display = (
        'user', 'recipe', 'date_added',
    )
    list_filter = (
        'user', 'recipe',
    )


@admin.register(ShoppingCard)
class ShoppingCardRecipeAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'ShoppingCard'."""
    list_display = (
        'user', 'recipe', 'date_added',
    )
    list_filter = (
        'user', 'recipe',
    )


class FavouriteRecipeInline(admin.StackedInline):
    """Инлайн для модели 'FavouriteRecipeInline'."""
    model = FavouriteRecipe
    extra = 0
    fields = ('recipe', 'date_added',)
    readonly_fields = ('date_added',)


class ShoppingCardInline(admin.StackedInline):
    """Инлайн для модели 'ShoppingCardInline'."""
    model = ShoppingCard
    extra = 0
    fields = ('recipe', 'date_added',)
    readonly_fields = ('date_added',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка панели администратора для модели 'User'."""
    inlines = (FavouriteRecipeInline, ShoppingCardInline,)
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
