from django.contrib.auth.models import AnonymousUser
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe
from users.models import User


class RecipeFilterSet(filters.FilterSet):
    """
    Позволяет фильтровать объекты модели Recipe
    по поля author, tags, is_favorited, is_in_shopping_cart.
    """
    author = filters.NumberFilter(
        field_name='author__id',
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
        method='filter_tags',
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        widget=BooleanWidget(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        widget=BooleanWidget(),
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
        ]

    def filter_tags(
            self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet[Recipe]:
        """
        Фильтрует рецепты по тегам.
        Позволяет использовать несколько значений тегов для фильтрации.
        """
        tags: list[str] = self.request.GET.getlist('tags', '')
        return queryset.filter(tags__slug__in=tags)

    def get_current_queryset(
            self, queryset: QuerySet, name: str,
            value: bool, user_field: str
    ):
        """
        Возвращает отфильтрованный QuerySet рецептов
        по связанному полю 'user_field' для текущего пользователя.
        """
        current_user: User = self.request.user
        if isinstance(current_user, AnonymousUser):
            return queryset
        filter_data: dict[str, bool, User] = {
            f'{user_field}__isnull': not value,
            f'{user_field}': current_user,
        }
        if value:
            return queryset.filter(**filter_data)
        filter_data[f'{user_field}__isnull'] = value
        return queryset.exclude(**filter_data)

    def filter_is_favorited(
            self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet[Recipe]:
        """
        Фильтрует рецепты по наличию/отсутствию в списке избранного
        для текущего пользователя.
        """
        return self.get_current_queryset(
            queryset, name, value, user_field='user_favourites'
        )

    def filter_is_in_shopping_cart(
            self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet[Recipe]:
        """
        Фильтрует рецепты по наличию/отсутствию в корзине
        для текущего пользователя.
        """
        return self.get_current_queryset(
            queryset, name, value, user_field='user_shopping_cart'
        )
