from collections import OrderedDict
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from .fields import Base64ImageField, IngredientRecipeWriteField
from .mixins import UserRecipeFieldsSet, SubscribedMethodField
from .validators import (
    tags_unique_validator, ingredients_exist_validator,
    ingredients_unique_validator, check_duplicate_recipe,
    get_ingredient_or_400, tags_exist_validator,
    recipe_exist_validator, post_request_user_recipe_validator
)
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredient
from users.models import User, FavouriteRecipe, ShoppingCard, Follow


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


class UserCustomSerializer(SubscribedMethodField, UserSerializer):
    """Сериализатор для модели User."""
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj: Follow) -> bool:
        """
        Определяет подаписан ли запрашиваемый пользователь на текущего.
        """
        return self._get_is_subscribed(obj)


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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сокращенный сериализатор для модели Ingredient."""
    class Meta:
        model = Recipe
        fields = (
            'id', 'name',
            'image', 'cooking_time',
        )
        read_only_fields = (
            'id', 'name',
            'image', 'cooking_time',
        )


class ShoppingCardSerializer(UserRecipeFieldsSet,
                             serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCard."""
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
        recipe: Recipe = recipe_exist_validator(self.context['request'])
        post_request_user_recipe_validator(
            ShoppingCard, self.context['request'].method,
            recipe, self.context['request'].user
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


class FavouriteRecipeSerializer(UserRecipeFieldsSet,
                                serializers.ModelSerializer):
    """Сериализатор для модели FavouriteRecipe."""
    class Meta:
        model = FavouriteRecipe
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
        recipe: Recipe = recipe_exist_validator(self.context['request'])
        post_request_user_recipe_validator(
            FavouriteRecipe, self.context['request'].method,
            recipe, self.context['request'].user
        )
        attrs['recipe'] = recipe
        return attrs

    def create(self, validated_data: dict[str, Any]) -> FavouriteRecipe:
        """
        Создает новый объект 'FavouriteRecipe'
        на основании валидированных данных.
        """
        return FavouriteRecipe.objects.create(
            user=self.context['request'].user,
            recipe=validated_data['recipe']
        )


class FollowSerializer(SubscribedMethodField, serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    id = serializers.IntegerField(
        source='following.id', read_only=True
    )
    username = serializers.CharField(
        source='following.username', read_only=True
    )
    first_name = serializers.CharField(
        source='following.first_name', read_only=True
    )
    last_name = serializers.CharField(
        source='following.last_name', read_only=True
    )
    email = serializers.EmailField(
        source='following.email', read_only=True
    )
    recipes = ShortRecipeSerializer(
        source='following.recipes',
        many=True, read_only=True
    )
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'recipes', 'recipes_count',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj: Follow) -> bool:
        """
        Определяет подаписан ли запрашиваемый пользователь на текущего.
        """
        return self._get_is_subscribed(obj.following)

    def get_recipes_count(self, obj: Follow) -> int:
        """Считает количество рецептов у подписки."""
        return (
            self.context['view']
            .get_queryset()
            .filter(following=obj.following)
            .values('following__recipes')
            .exclude(following__recipes__isnull=True)
            .count()
        )

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет валидность данных перед созданием объекта Follow.
        """
        user: User = self.context['request'].user
        following: User = self.context['view'].get_following()
        if user.id == following.id:
            raise serializers.ValidationError(
                {
                    'follow': 'На себя подписаться нельзя.'
                }
            )
        if Follow.objects.filter(
            user=user, following=following
        ).exists():
            raise serializers.ValidationError(
                {
                    'follow': 'Вы уже подписаны на этого пользователя.'
                }
            )
        attrs['user'] = user
        attrs['following'] = following
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Follow:
        """
        Создает объект Follow на основе проверенных данных.
        """
        return Follow.objects.create(
            user=validated_data['user'],
            following=validated_data['following']
        )

    def to_representation(self, instance: Follow) -> dict[str, Any]:
        """
        Метода для изменения представления экземпляров Follow
        с ограничением по количеству рецептов (если применимо).
        """
        data: dict[str, Any] = super().to_representation(instance)
        recipes_limit: str | None = (
            self.context['request']
            .query_params.get('recipes_limit')
        )
        recipes: list[OrderedDict[Recipe]] = data['recipes']
        if recipes_limit and recipes and len(recipes) > int(recipes_limit):
            data['recipes'] = recipes[:int(recipes_limit)]
        return data
