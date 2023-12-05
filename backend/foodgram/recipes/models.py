from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from .managers import RecipeManager
from core.models import NameString

more_zero = MinValueValidator(1)

User = get_user_model()


class Tag(NameString, models.Model):
    """Модель для хранения информации о тэгах."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Наименование',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        unique=True,
        max_length=100,
        verbose_name='Идентификатор',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)


class Ingredient(NameString, models.Model):
    """Модель для хранения информации об ингредиентах."""
    measurement_unit = models.CharField(
        max_length=10,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)


class Recipe(NameString, models.Model):
    """Модель для хранения информации о рецептах."""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Обложка рецепта',
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[more_zero]
    )

    objects = models.Manager()
    with_related = RecipeManager()

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        unique_together = ('name', 'author',)


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для хранения связи
    между рецептами и ингредиентами.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[more_zero]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        unique_together = ('recipe', 'ingredient',)

    def __str__(self) -> str:
        """
        Возвращает строковое предсталение при обращении к объекту.
        """
        return (
            f'Ингредиент "{self.ingredient.name}" '
            f'к рецепту "{self.recipe.name}"'
        )
