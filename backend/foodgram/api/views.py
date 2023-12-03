from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilterSet
from .mixins import GetNonePaginatorAllowAny
from .permissions import IsAuthor
from .serializers import (
    UserCustomSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    ShoppingCardSerializer
)
from .validators import valide_shopping_card
from recipes.models import Tag, Ingredient, Recipe
from users.models import ShoppingCard


class UserCustomViewSet(UserViewSet):
    """Представление, отвечающее за работу с пользователями в системе."""
    http_method_names = ['get', 'post',]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request) -> Response:
        """Получает информацию о текущем авторизованном пользователе."""
        serializer: UserCustomSerializer = self.get_serializer(request.user)
        return Response(serializer.data)


class TagViewSet(GetNonePaginatorAllowAny, ModelViewSet):
    """Представление, отвечающее за работу с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(GetNonePaginatorAllowAny, ModelViewSet):
    """Представление, отвечающее за работу с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self) -> QuerySet:
        """
        Получает QuerySet.
        Если указан параметр 'name', фильтрует по имени.
        """
        queryset: QuerySet = super().get_queryset()
        name_param: str = self.request.query_params.get('name')
        if name_param:
            queryset: QuerySet = (
                queryset.filter(name__istartswith=name_param)
                | queryset.filter(name__icontains=name_param)
            )
        return queryset


class RecipeViewSet(ModelViewSet):
    """Представление, отвечающее за работу с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthor
    ]
    filterset_class = RecipeFilterSet
    http_method_names = [
        'get', 'post',
        'patch', 'delete'
    ]

    def perform_create(self, serializer: RecipeSerializer) -> None:
        """Создаем рецепт и присваем текущего пользователя."""
        serializer.save(author=self.request.user)


class ShoppingCardViewSet(ModelViewSet):
    """Представление, отвечающее за работу с корзиной покупок."""
    queryset = ShoppingCard.objects.all()
    serializer_class = ShoppingCardSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']
    lookup_url_kwarg = 'id'

    def get_recipe(self) -> Recipe:
        """Получает объект рецепта из URL."""
        return get_object_or_404(
            Recipe, id=self.kwargs.get('id')
        )

    def get_object(self) -> ShoppingCard | None:
        """Получает объект корзины пользователя."""
        try:
            return ShoppingCard.objects.filter(
                user=self.request.user,
                recipe=self.get_recipe()
            )
        except ShoppingCard.DoesNotExist:
            return None

    def perform_destroy(
            self, instance: ShoppingCard
    ) -> None | ValidationError:
        """Удаляет объект корзины покупок пользователя."""
        valide_shopping_card(instance)
        instance.delete()
