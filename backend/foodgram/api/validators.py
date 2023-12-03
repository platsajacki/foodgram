from collections import OrderedDict

from rest_framework.serializers import ValidationError
from rest_framework.request import Request

from recipes.models import Tag, Recipe, Ingredient
from users.models import ShoppingCard


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


def valide_shopping_card(
        shoping_card: ShoppingCard | None
) -> ValidationError | None:
    """Проверяет наличие рецепта в корзине покупок."""
    if not shoping_card:
        raise ValidationError(
            {
                'shopping_card': 'Рецепта не было в списке покупок.'
            }
        )
