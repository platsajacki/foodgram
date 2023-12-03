from collections import OrderedDict
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .fields import Base64ImageField, IngredientRecipeWriteField
from .validators import (
    tags_unique_validator, ingredients_exist_validator,
    ingredients_unique_validator, check_duplicate_recipe,
    get_ingredient_or_400, tags_exist_validator
)
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
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
    image = Base64ImageField()
    ingredients = IngredientRecipeWriteField(
        write_only=True, many=True
    )
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

    def validate(
            self, attrs: dict[str, Any]
    ) -> dict[str, Any] | serializers.ValidationError:
        """Проверяет входные данные."""
        instance: Recipe | None = self.instance
        check_duplicate_recipe(
            self.context['request'],
            attrs['name'], instance
        )
        ingredients: list[OrderedDict[str, int]] = attrs.get('ingredients')
        ingredients_exist_validator(ingredients)
        ingredients_unique_validator(ingredients)
        tags: list[Tag] = attrs.get('tags')
        tags_exist_validator(tags)
        tags_unique_validator(tags)
        return attrs

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
        tags_data: list[dict] = []
        for tag in instance.tags.all():
            tags_data.append(TagSerializer(tag).data)
        representation['ingredients'] = ingredient_data
        representation['tags'] = tags_data
        return representation

    def create(self, validated_data: dict[str, Any]) -> Recipe:
        """
        Создает новый объект 'Recipe'
        на основании валидированных данных.
        """
        ingredients_data: list[OrderedDict[str, int]] = (
            validated_data.pop('ingredients')
        )
        tags_data: list[Tag] = validated_data.pop('tags')
        for ingredient_data in ingredients_data:
            ingredient_data['ingredient'] = (
                get_ingredient_or_400(ingredient_data['ingredient'])
            )
        recipe: Recipe = Recipe.objects.create(**validated_data)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        recipe.tags.set(tags_data)
        return recipe

    def update(
            self, instance: Recipe, validated_data: dict[str, Any]
    ) -> Recipe:
        """
        Обновляет объект 'Recipe'
        на основании валидированных данных.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = (
            validated_data.get('cooking_time', instance.cooking_time)
        )
        instance.image = validated_data.get('image', instance.image)
        ingredients_data: list[OrderedDict[str, int]] = (
            validated_data.get('ingredients')
        )
        if ingredients_data:
            recipe_ingredients = []
            for ingredient_data in ingredients_data:
                ingredient: Ingredient = (
                    get_ingredient_or_400(ingredient_data['ingredient'])
                )
                recipe_ingredients.append(
                    RecipeIngredient(
                        recipe=instance,
                        ingredient=ingredient,
                        amount=ingredient_data['amount'],
                    )
                )
            RecipeIngredient.objects.filter(recipe=instance).delete()
            RecipeIngredient.objects.bulk_create(recipe_ingredients)
        tags_data: list[Tag] = validated_data.get('tags')
        if tags_data:
            instance.tags.clear()
            instance.tags.set(tags_data)
        instance.save()
        return instance


class ShoppingCardSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCard."""
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

    class Meta:
        model = ShoppingCard
        fields = (
            'id', 'name',
            'image', 'cooking_time',
        )

    def validate(
            self, attrs: dict[str, Any]
    ) -> dict[str, Any] | serializers.ValidationError:
        """
        Проверяет входные данные,
        проверяет рецепт и добавляет его к 'attrs'.
        """
        id: int = (
            self.context['request']
            .parser_context.get('kwargs')
            .get('id')
        )
        method: str = self.context['request'].method
        try:
            recipe: Recipe = Recipe.objects.get(id=id)
        except Recipe.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'recipe': 'Такого рецепта не существует.'
                }
            )
        shoping_card_exists: ShoppingCard = (
            ShoppingCard.objects.filter(
                user=self.context['request'].user,
                recipe=recipe
            ).exists()
        )
        if method == 'POST' and shoping_card_exists:
            raise serializers.ValidationError(
                {
                    'shopping_card': 'Рецепт уже есть в списке покупок.'
                }
            )
        attrs['recipe'] = recipe
        return attrs

    def create(self, validated_data: dict[str, Any]) -> ShoppingCard:
        """
        Создает новый объект 'ShoppingCard'
        на основании валидированных данных.
        """
        return ShoppingCard.objects.create(
            user=self.context['request'].user,
            recipe=validated_data['recipe']
        )
