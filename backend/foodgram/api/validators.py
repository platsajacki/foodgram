from collections import OrderedDict

from rest_framework.serializers import ValidationError
from rest_framework.request import Request

from recipes.models import Tag, Recipe


def tags_unique_validator(value: list[Tag]) -> None | ValidationError:
    """Проверяет уникальность тегов."""
    if len(value) > len(set(value)):
        raise ValidationError(
            {
                'tags':
                'Каждый тег должен быть уникальным.'
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
        request: Request, name: str
) -> None | ValidationError:
    """Проверка рецептов на дублирование."""
    if (
        request.method in ['POST', 'PATCH']
        and Recipe.objects.filter(author=request.user, name=name)
    ):
        raise ValidationError(
                {
                    'recipe':
                    'Такой рецепт уже существует.'
                }
            )
