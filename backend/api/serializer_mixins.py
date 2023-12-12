from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers


class UserRecipeFieldsSet(serializers.Serializer):
    """
    Миксин сериализатора для извлечения
    ID, название, изображение и время приготовления экземпляра рецепта.
    """
    id = serializers.IntegerField(
        source='recipe.id', read_only=True
    )
    name = serializers.CharField(
        source='recipe.name', read_only=True
    )
    image = Base64ImageField(
        source='recipe.image', read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )
