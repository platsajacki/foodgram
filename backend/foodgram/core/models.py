from django.db import models


class NameString(models.Model):
    """
    Абстарктная модель с полем 'name'
    и его строковым представлением.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Наименование',
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """
        Возвращает строкового предсталение поля
        'name' при обращении к объекту.
        """
        return self.name


class UserRecipe(models.Model):
    """
    Абстрактная модель для связи пользователей и рецептов.
    """
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        'recipes.Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class DateAdded(models.Model):
    """
    Абстрактная модель с полем date_added.
    """
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        abstract = True
