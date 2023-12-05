from django.db.models import QuerySet, Manager


class RecipeQuerySet(QuerySet):
    """QuerySet для работы с моделью Recipe."""
    def related_tables(self) -> 'RecipeQuerySet':
        """
        Отимизирует запрос, присоединяя таблицы.
        """
        return (
            self
            .select_related('author')
            .prefetch_related(
                'tags', 'ingredients', 'recipeingredient_set__ingredient',
                'favouriterecipe_set__user', 'shoppingcard_set__user'
            )
        )


class RecipeManager(Manager):
    """Manager для работы с моделью Recipe."""
    def get_queryset(self) -> 'RecipeManager':
        """
        Возвращает QuerySet для модели Recipe
        с выбранными связанными таблицами.
        """
        return (
            RecipeQuerySet(self.model)
            .related_tables()
        )
