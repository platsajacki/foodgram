from rest_framework import serializers

from recipes.models import RecipeIngredient


class IngredientRecipeWriteField(serializers.ModelSerializer):
    """Сериализатор для записи данных о ингредиентах рецепта."""
    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)
        write_only_fields = ('id', 'amount',)
