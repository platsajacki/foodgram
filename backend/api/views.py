from datetime import date
from io import BytesIO
from typing import Any

from django.db.models import QuerySet, Prefetch
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
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
from .mixins import GetNonePaginatorAllowAny, UserRecipeViewSet
from .permissions import IsAuthor
from .serializers import (
    UserSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    ShoppingCartSerializer, FavoriteRecipeSerializer,
    FollowSerializer
)
from .utils import get_xls_shopping_cart
from recipes.models import Tag, Ingredient, Recipe
from users.models import User, ShoppingCart, FavoriteRecipe, Follow


class UserViewSet(DjoserUserViewSet):
    """Представление, отвечающее за работу с пользователями в системе."""
    http_method_names = ['get', 'post']

    def get_queryset(self) -> QuerySet:
        """
        Получает запрос для модели и выполняет предварительную загрузку
        связанных объектов Follow для текущего пользователя.
        """
        if not self.request.user.is_authenticated:
            return User.objects.all()
        return User.objects.prefetch_related(
            Prefetch(
                'followings',
                queryset=(
                    Follow.with_related
                    .filter(user=self.request.user)
                ),
                to_attr='follower'
            )
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request) -> Response:
        """Получает информацию о текущем авторизованном пользователе."""
        user: User = self.get_queryset().get(id=request.user.id)
        serializer: UserSerializer = self.get_serializer(user)
        return Response(serializer.data)


class TagViewSet(GetNonePaginatorAllowAny, ModelViewSet):
    """Представление, отвечающее за работу с тегами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(GetNonePaginatorAllowAny, ModelViewSet):
    """Представление, отвечающее за работу с ингредиентами."""
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self) -> QuerySet:
        """
        Получает QuerySet.
        Если указан параметр 'name', фильтрует по имени.
        """
        queryset: QuerySet = Ingredient.objects.all()
        name_param: str = self.request.query_params.get('name')
        if name_param:
            queryset: QuerySet = queryset.filter(name__istartswith=name_param)
        return queryset


class RecipeViewSet(ModelViewSet):
    """Представление, отвечающее за работу с рецептами."""
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

    def get_queryset(self) -> QuerySet:
        """
        Получает запрос для модели и выполняет предварительную загрузку
        связанных объектов Follow, Ingredient, Tag для текущего пользователя.
        """
        if not self.request.user.is_authenticated:
            return Recipe.with_related.all()
        return (
            Recipe.with_related
            .prefetch_related(
                Prefetch(
                    'author__followings',
                    queryset=(
                        Follow.with_related
                        .filter(user=self.request.user)
                    ),
                    to_attr='follower'
                )
            )
            .annotate_user_flags(user=self.request.user)
        )

    def perform_create(self, serializer: RecipeSerializer) -> None:
        """Создаем рецепт и присваем текущего пользователя."""
        serializer.save(author=self.request.user)


class ShoppingCartViewSet(UserRecipeViewSet, ModelViewSet):
    """Представление, отвечающее за работу с корзиной покупок."""
    queryset = ShoppingCart.objects.select_related('user', 'recipe')
    serializer_class = ShoppingCartSerializer
    http_method_names = ['get', 'post', 'delete']

    def download_shopping_cart(self, request: Request):
        """
        Метод для скачивания списка покупок
        в формате Excel (XLS) при GET запросе.
        """
        ingredients: QuerySet = (
            ShoppingCart.objects
            .filter(user=request.user)
            .get_ingredients_shoppingcart()
        )
        buffer: BytesIO = get_xls_shopping_cart(ingredients)
        today: date = timezone.now().date()
        return FileResponse(buffer, filename=f'Список покупок_{today}.xls')


class FavoriteRecipeViewSet(UserRecipeViewSet, ModelViewSet):
    """Представление, отвечающее за работу с избранным."""
    queryset = FavoriteRecipe.objects.select_related('user', 'recipe')
    serializer_class = FavoriteRecipeSerializer
    http_method_names = ['post', 'delete']


class FollowViewSet(ModelViewSet):
    """Представление, отвечающее за работу с подписками."""
    serializer_class = FollowSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Возвращает QuerySet объектов Follow,
        связанных с запрашивающим пользователем.
        """
        return (
            Follow.with_related
            .filter(user=self.request.user)
            .prefetch_related('following__recipes')
            .all()
        )

    def get_following(self) -> User:
        """Получает подписку."""
        return get_object_or_404(
            User, id=self.kwargs.get('id')
        )

    def get_object(self) -> Follow:
        """Получает объект связанной модели подписки."""
        return get_object_or_404(
            Follow.objects,
            user=self.request.user,
            following=self.get_following()
        )

    def destroy(
            self, request: Request, *args: Any, **kwargs: dict[str, Any]
    ) -> Response | ValidationError:
        """Удаляет объект, если он существует."""
        following: User = self.get_following()
        try:
            instance: Follow = Follow.objects.get(
                user=request.user,
                following=following
            )
        except Follow.DoesNotExist:
            raise ValidationError(
                {
                    'follow': 'Вы не были подписаны на данного пользователя.'
                }
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
