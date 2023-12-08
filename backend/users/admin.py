from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow, ShoppingCart, FavouriteRecipe


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
        'user', 'recipe__name', 'date_added',
    )


@admin.register(ShoppingCart)
class ShoppingCartRecipeAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'ShoppingCart'."""
    list_display = (
        'user', 'recipe', 'date_added',
    )
    list_filter = (
        'user', 'recipe__name', 'date_added',
    )


class FavouriteRecipeInline(admin.StackedInline):
    """Инлайн для модели 'FavouriteRecipeInline'."""
    model = FavouriteRecipe
    extra = 0
    fields = ('recipe', 'date_added',)
    readonly_fields = ('date_added',)


class ShoppingCartInline(admin.StackedInline):
    """Инлайн для модели 'ShoppingCartInline'."""
    model = ShoppingCart
    extra = 0
    fields = ('recipe', 'date_added',)
    readonly_fields = ('date_added',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Настройка панели администратора для модели 'User'."""
    inlines = (FavouriteRecipeInline, ShoppingCartInline,)
    add_fieldsets = (
        ('Регистрация пользователя', {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name',
                'email', 'password1',
            ),
        }),
    )
    list_filter = UserAdmin.list_filter + ('username', 'email',)
