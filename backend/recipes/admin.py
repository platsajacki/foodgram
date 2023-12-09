from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import FavoriteRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'Ingredient'."""
    list_display = (
        'name', 'measurement_unit'
    )
    list_filter = ('name',)
    fields = (
        'name', 'measurement_unit',
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'Tag'."""
    list_display = (
        'name', 'color', 'slug'
    )
    list_filter = ('name',)
    fields = (
        'name', 'color', 'slug'
    )


class RecipeIngredientInline(admin.TabularInline):
    """Инлайн для модели 'RecipeIngredient'."""
    model = RecipeIngredient
    extra = 0
    fields = (
        'ingredient', 'amount', 'measurement_unit'
    )
    readonly_fields = ('measurement_unit',)

    def measurement_unit(self, instance: Recipe) -> str:
        """
        Возвращает единицу измерения для конкретного ингредиента в рецепте.
        """
        return instance.ingredient.measurement_unit

    measurement_unit.short_description = 'Единица измерения'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройка панели администратора для модели 'Recipe'."""
    inlines = (RecipeIngredientInline,)
    list_display = (
        'name', 'author'
    )
    list_filter = (
        'author', 'name', 'tags',
    )
    fields = (
        'name', 'author', 'image',
        'text', 'tags', 'cooking_time',
        'favorites_count',
    )
    readonly_fields = ('favorites_count',)

    def favorites_count(self, instance: Recipe) -> int:
        """Возвращает количество добавлений рецепта в избранное."""
        return FavoriteRecipe.objects.filter(recipe=instance).count()

    favorites_count.short_description = 'Количество добавлений в избранное'
