from typing import Any

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя."""
    use_in_migrations: bool = True

    def _create_user(
        self, username: str, email: str, password: str,
        first_name: str, last_name: str, **extra_fields: Any
    ):
        """
        Создает и сохраняет пользователя с username, email,
        first_name, last_name, и password для суперпользователя.
        """
        if not username:
            raise ValueError('Необходимо указать имя пользователя (логин).')
        if not email:
            raise ValueError('Необходимо указать электронную почту.')
        if not first_name:
            raise ValueError('Необходимо указать имя.')
        if not last_name:
            raise ValueError('Необходимо указать фамилию.')
        email: str = self.normalize_email(email)
        user: self.model = self.model(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, username: str, email: str, password: str,
        first_name: str, last_name: str, **extra_fields: Any
    ):
        """Создает и сохраняет обычного пользователя."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

    def create_superuser(
        self, username: str, email: str, password: str,
        first_name: str, last_name: str, **extra_fields: Any
    ):
        """Создает и сохраняет суперпользователя."""
        extra_fields.setdefault(
            'is_staff', True
        )
        extra_fields.setdefault(
            'is_superuser', True
        )
        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True.'
            )
        return self._create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
