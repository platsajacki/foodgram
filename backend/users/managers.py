from django.apps import apps
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db.models import QuerySet, Manager, Sum, Exists, OuterRef


class UserManager(DjangoUserManager):
    """Кастомный менеджер для модели пользователя."""
    def add_is_subscribed(self, user) -> QuerySet:
        """
        Аннотирует запрос для проверки подписки
        пользователя на других пользователей.
        """
        return (
            self.annotate(
                is_subscribed=Exists(
                    queryset=apps.get_model(
                        app_label='users', model_name='Follow'
                    )
                    .with_related
                    .filter(
                        user=user,
                        following=OuterRef('pk')
                    )
                )
            )
        )


class FollowQuerySet(QuerySet):
    """QuerySet для работы с моделью Follow."""
    def related_tables(self) -> 'FollowQuerySet':
        """Отимизирует запрос, присоединяя таблицы."""
        return (
            self
            .select_related('following', 'user')
            .prefetch_related(
                'following', 'user', 'following__recipes'
            )
        )


class FollowManager(Manager):
    """Manager для работы с моделью Follow."""
    def get_queryset(self) -> 'FollowManager':
        """
        Возвращает QuerySet для модели Follow
        с выбранными связанными таблицами.
        """
        return (
            FollowQuerySet(self.model)
            .related_tables()
        )


class ShoppingCartQuerySet(QuerySet):
    """QuerySet для работы с моделью ShoppingCart."""
    def get_ingredients_shoppingcart(self) -> 'ShoppingCartQuerySet':
        """
        Получает ингредиенты, их количство и единицу измерения
        для корзины покупок.
        """
        return (
            self
            .values(
                'recipe__recipeingredient__ingredient__name',
            )
            .annotate(
                total_amount=Sum(
                    'recipe__recipeingredient__amount',
                )
            )
            .order_by(
                'recipe__recipeingredient__ingredient__name',
            )
            .values(
                'recipe__recipeingredient__ingredient__measurement_unit',
                'recipe__recipeingredient__ingredient__name',
                'total_amount',
            )
        )
