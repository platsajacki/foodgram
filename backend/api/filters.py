from django.db.models import QuerySet
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe, Tag, Ingredient


class IngredientFilterSet(filters.FilterSet):
    """
    Фильтрует набор данных ингредиентов по имени, используя istartswith.
    """
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilterSet(filters.FilterSet):
    """
    Позволяет фильтровать объекты модели Recipe
    по поля author, tags, is_favorited, is_in_shopping_cart.
    """
    author = filters.NumberFilter(
        field_name='author__id',
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
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

    def filter_is_favorited(
            self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet[Recipe]:
        """
        Фильтрует рецепты по наличию/отсутствию в списке избранного
        для текущего пользователя.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(is_favorited=True)
        return queryset

    def filter_is_in_shopping_cart(
            self, queryset: QuerySet, name: str, value: bool
    ) -> QuerySet[Recipe]:
        """
        Фильтрует рецепты по наличию/отсутствию в корзине
        для текущего пользователя.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(is_in_shopping_cart=True)
        return queryset
