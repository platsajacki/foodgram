from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Follow, ShoppingCart, FavoriteRecipe


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'Follow'."""
    list_display = (
        'user', 'following', 'date_added',
    )
    list_filter = (
        'user', 'following',
    )


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'FavoriteRecipe'."""
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


class FavoriteRecipeInline(admin.StackedInline):
    """Инлайн для модели 'FavoriteRecipeInline'."""
    model = FavoriteRecipe
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
class UserAdmin(DjangoUserAdmin):
    """Настройка панели администратора для модели 'User'."""
    inlines = (FavoriteRecipeInline, ShoppingCartInline,)
    add_fieldsets = (
        ('Регистрация пользователя', {
            'classes': ('wide',),
            'fields': (
                'username', 'first_name', 'last_name',
                'email', 'password1', 'password2',
            ),
        }),
    )
    list_filter = DjangoUserAdmin.list_filter + ('username', 'email',)
