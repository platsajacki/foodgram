from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .fields import Base64ImageField
from recipes.models import Tag, Ingredient, Recipe
from users.models import User, Follow, FavouriteRecipe, ShoppingCard


class UserCustomCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для регистрации пользователя,
    который учитывает недопустимость username со значением 'me'.
    """
    def validate_username(self, value: str) -> str:
        """Проверка имени пользователя на недопустимые значения."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" недопустимо.'
            )
        return value


class UserCustomSerializer(UserSerializer):
    """Сериализатор для модели User."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj: User) -> bool:
        """
        Определяет подаписан ли запрашиваемый пользователь на текущего.
        В случае, если пользователь анонимный, возвращается 'False'.
        """
        current_user: User = self.context['request'].user
        if isinstance(current_user, AnonymousUser):
            return False
        return (
            Follow.objects
            .filter(
                user=current_user,
                following=obj
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = (
            'id', 'name',
            'color', 'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = (
            'id', 'name',
            'measurement_unit',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    author = UserCustomSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'author', 'image',
            'text', 'cooking_time',
            'ingredients', 'tags',
            'is_favorited', 'is_in_shopping_cart',
        )

    def relate_user_recipe(self, obj: Recipe, related_model: Model) -> bool:
        """Определяет, связан ли текущий пользователь с переданным рецептом."""
        current_user: User = self.context['request'].user
        if isinstance(current_user, AnonymousUser):
            return False
        return (
            related_model.objects
            .filter(
                user=current_user,
                recipe=obj,
            ).exists()
        )

    def get_is_favorited(self, obj: Recipe) -> bool:
        """
        Получает информацию, отмечен ли переданный рецепт
        как избранный для текущего пользователя.
        """
        return self.relate_user_recipe(obj, FavouriteRecipe)

    def get_is_in_shopping_cart(self, obj: Recipe) -> bool:
        """
        Получает информацию, находится ли переданный рецепт
        в списке покупок текущего пользователя.
        """
        return self.relate_user_recipe(obj, ShoppingCard)

    def to_representation(self, instance: Recipe) -> dict[str, str]:
        """Готовит данные для отправки в ответе."""
        representation: dict[str, str] = super().to_representation(instance)
        ingredient_data: list[dict] = []
        for recipe_ingredient in instance.recipeingredient_set.all():
            ingredient: dict[str, Any] = {
                'id': recipe_ingredient.ingredient.id,
                'name': recipe_ingredient.ingredient.name,
                'measurement_unit': (
                    recipe_ingredient.ingredient.measurement_unit
                ),
                'amount': recipe_ingredient.amount,
            }
            ingredient_data.append(ingredient)
        representation['ingredients'] = ingredient_data
        return representation

    # def create(self, validated_data: dict[str, Any]):
    #     return super().create(validated_data)

    # def update(self, instance: Recipe, validated_data: dict[str, Any]):
    #     return super().update(instance, validated_data)
