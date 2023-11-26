from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    """Модель для хранения информации о пользователях."""
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        blank=False,
    )
    email = models.EmailField(
        verbose_name='Электроный адрес',
        blank=False,
    )

    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']
