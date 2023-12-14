from django.db.models import QuerySet, Manager, Exists, OuterRef, Prefetch

from users.models import User, Follow


class RecipeQuerySet(QuerySet):
    """QuerySet для работы с моделью Recipe."""
    def related_tables(self) -> 'RecipeQuerySet':
        """
        Отимизирует запрос, присоединяя таблицы.
        """
        return (
            self
            .prefetch_related(
                'tags', 'recipeingredient_set__ingredient',
                'favoriterecipe_set', 'shoppingcart_set',
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

    def annotate_user_flags(self, user: User) -> 'RecipeQuerySet':
        """
        Аннотирует флаги пользователя для рецептов,
        проверяя, есть ли рецепт в его списке избранного
        или корзине покупок.
        """
        return (
            self
            .annotate(
                is_in_shopping_cart=Exists(
                    queryset=User.objects.filter(
                        id=user.id,
                        shopping_cart=OuterRef('pk')
                    )
                )
            )
            .annotate(
                is_favorited=Exists(
                    queryset=User.objects.filter(
                        id=user.id,
                        favorites=OuterRef('pk')
                    )
                )
            )
            .prefetch_related(
                Prefetch(
                    'author',
                    queryset=User.objects.annotate(
                        is_subscribed=Exists(
                            queryset=(
                                Follow.with_related
                                .filter(
                                    user=user,
                                    following=OuterRef('pk')
                                )
                            )
                        )
                    )
                )
            )
        )
