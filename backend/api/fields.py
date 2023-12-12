from rest_framework import serializers

from recipes.models import RecipeIngredient


class IngredientRecipeWriteField(serializers.ModelSerializer):
    """Сериализатор для записи данных о ингредиентах рецепта."""
    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class IngredientRecipeReadField(serializers.ModelSerializer):
    """Сериализатор для чтения данных о ингредиентах рецепта."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit',)
