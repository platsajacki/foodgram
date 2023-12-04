from collections import OrderedDict

from django.db.models import Model
from rest_framework.serializers import ValidationError
from rest_framework.request import Request

from recipes.models import Tag, Recipe, Ingredient
from users.models import User


def tags_unique_validator(value: list[Tag]) -> None | ValidationError:
    """Проверяет уникальность тегов."""
    if len(value) > len(set(value)):
        raise ValidationError(
            {
                'tags':
                'Каждый тег должен быть уникальным.'
            }
        )


def tags_exist_validator(value: list[Tag]) -> None | ValidationError:
    """Проверяет наличие ингредиентов в запросе."""
    if not value:
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
    if not value:
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
    seen_ingredients: set = set()
    for item in value:
        ingredient_id: int = item.get('ingredient')
        if ingredient_id in seen_ingredients:
            raise ValidationError(
                {
                    'ingredients':
                    'Каждый ингредиент должен быть уникальным.'
                }
            )
        seen_ingredients.add(ingredient_id)


def check_duplicate_recipe(
        request: Request, name: str, instance: Recipe | None
) -> None | ValidationError:
    """Проверка рецептов на дублирование."""
    error: ValidationError = ValidationError(
        {
            'recipe':
            'У Вас уже существует рецепт с таким названием.'
        }
    )
    if request.method in ['POST', 'PATCH']:
        recipe: Recipe = Recipe.objects.filter(author=request.user, name=name)
        if instance and recipe.exclude(id=instance.id).exists():
            raise error
        if recipe.exists():
            raise error


def get_ingredient_or_400(id: int) -> Ingredient | ValidationError:
    """
    Получает объект ингредиента по его ID
    или вызывает 'ValidationError', если объекта не существует.
    """
    try:
        ingredient: Ingredient = Ingredient.objects.get(id=id)
    except Ingredient.DoesNotExist:
        raise ValidationError(
            {
                'ingredients': 'Такого ингредиента не существует.'
            }
        )
    return ingredient


def valide_user_has_recipe(
        related_model: Model | None
) -> ValidationError | None:
    """Проверяет наличие рецепта в у пользователя."""
    if not related_model:
        raise ValidationError(
            {
                'recipe': 'Рецепт не был ранее добавлен.'
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
