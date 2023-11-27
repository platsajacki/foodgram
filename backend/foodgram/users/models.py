from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager
from core.models import UserRecipe, DateAdded


class User(AbstractUser):
    """Модель для хранения информации о пользователях."""
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    email = models.EmailField(
        verbose_name='Электроный адрес',
        unique=True,
    )
    favourites = models.ManyToManyField(
        'recipes.Recipe',
        through='FavouriteRecipe',
        related_name='user_favourites',
        verbose_name='Избранное',
    )
    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        through='ShoppingCard',
        related_name='user_shopping_cart',
        verbose_name='Корзина',
    )

    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']


class Follow(DateAdded, models.Model):
    """Связанная модель для реализации системы подписок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followings'
    )

    class Meta:
        unique_together = ['user', 'following']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        """
        Возвращает строковое предсталение при обращении к объекту.
        """
        return (
            f'{self.user.first_name} {self.user.last_name} подписан(а) на '
            f'{self.following.first_name} {self.following.last_name}'
        )


class FavouriteRecipe(UserRecipe, DateAdded, models.Model):
    """
    Промежуточная модель для хранения связи
    пользователя и его избранных рецептов.
    """
    class Meta:
        ordering = ['-date_added', 'user']
        unique_together = ['user', 'recipe']
        verbose_name = 'Избранный товар'
        verbose_name_plural = 'Избранное'

    def __str__(self) -> str:
        """
        Возвращает строковое предсталение при обращении к объекту.
        """
        return f'Избранное {self.user.first_name} {self.user.last_name}'


class ShoppingCard(UserRecipe, DateAdded, models.Model):
    """
    Промежуточная модель для хранения связи
    пользователя и рецептов в его корзине.
    """
    class Meta:
        ordering = ['-date_added', 'user']
        unique_together = ['user', 'recipe']
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Корзины'

    def __str__(self) -> str:
        """
        Возвращает строковое предсталение при обращении к объекту.
        """
        return f'Корзина {self.user.first_name} {self.user.last_name}'
