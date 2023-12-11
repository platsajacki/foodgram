from collections import OrderedDict
from typing import Any

from django.db.models import Model
from rest_framework.serializers import ValidationError
from rest_framework.request import Request

from recipes.models import Tag, Recipe, Ingredient
from users.models import User


def tags_unique_validator(
        value: list[OrderedDict[str, int]]
) -> None | ValidationError:
    """Проверяет уникальность тегов."""
    tags: list[Tag] = value.get('tags')
    if len(tags) > len(set(tags)):
        raise ValidationError(
            {
                'tags':
                'Каждый тег должен быть уникальным.'
            }
        )


def tags_exist_validator(
        value: list[OrderedDict[str, int]]
) -> None | ValidationError:
    """Проверяет наличие ингредиентов в запросе."""
    if not value.get('tags'):
        raise ValidationError(
            {
                'tags':
                'Необходимо указать тег(и) для создания рецепта.'
            }
        )


def ingredients_exist_validator(
        value: list[OrderedDict[str, int]]
) -> None | ValidationError:
    """Проверяет наличие ингредиентов в запросе."""
    if not value.get('ingredients'):
        raise ValidationError(
            {
                'ingredients':
                'Необходимо указать ингредиенты для создания рецепта.'
            }
        )


def ingredients_unique_validator(
        value: list[OrderedDict[str, int]]
) -> None | ValidationError:
    """
    Проверяет уникальность ингредиентов
    по ключу 'ingredient' в списке OrderedDict.
    """
    ingredients: list[OrderedDict[str, int]] = value.get('ingredients')
    seen_ingredients: set = set()
    for item in ingredients:
        ingredient_id: int = item.get('ingredient')
        if ingredient_id in seen_ingredients:
            raise ValidationError(
                {
                    'ingredients':
                    'Каждый ингредиент должен быть уникальным.'
                }
            )
        seen_ingredients.add(ingredient_id)


def get_ingredient_or_400(
        all_id: tuple[int], id: int
) -> Ingredient | ValidationError:
    """
    Получает объект ингредиента по его ID
    или вызывает 'ValidationError', если объекта не существует.
    """
    print(id, all_id)
    if id not in all_id:
        raise ValidationError(
            {
                'ingredients': 'Такого ингредиента не существует.'
            }
        )


def recipe_exist_validator(request: Request) -> Recipe | ValidationError:
    """
    Проверяет наличие рецепта в базе и возвращает его или ValidationError.
    """
    id: int = (
        request
        .parser_context.get('kwargs')
        .get('id')
    )
    try:
        recipe: Recipe = Recipe.objects.get(id=id)
    except Recipe.DoesNotExist:
        raise ValidationError(
            {
                'recipe': 'Такого рецепта не существует.'
            }
        )
    return recipe


def post_request_user_recipe_validator(
        related_model: Model, method: str,
        recipe: Recipe, user: User
) -> None | ValidationError:
    """
    Проверяет есть ли уже связь
    объектов пользователя и рецепта в базу.
    """
    model_related_exists: bool = (
        related_model.objects.filter(
            user=user,
            recipe=recipe
        ).exists()
    )
    if method == 'POST' and model_related_exists:
        raise ValidationError(
            {
                'recipe': 'Этот рецепт уже добавлен.'
            }
        )


def valide_image_exists(value: str | Any) -> None | ValidationError:
    """Проверяет наличие изображения."""
    if not value:
        raise ValidationError(
            {
                'image':
                'Без изображение блюда нельзя опубликовать рецепт.'
            }
        )
