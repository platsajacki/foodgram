from datetime import date
from io import BytesIO

from django.db.models import QuerySet, Exists, OuterRef
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilterSet
from .permissions import IsAuthor
from .serializers import (
    UserSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    ShoppingCartSerializer, FavoriteRecipeSerializer,
    FollowSerializer
)
from .view_mixins import GetNonePaginatorAllowAny, UserRecipeViewSet
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
        return (
            User.objects
            .annotate(
                is_subscribed=Exists(
                    queryset=Follow.with_related
                    .filter(
                        user=self.request.user,
                        following=OuterRef('pk')
                    )
                )
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
            return Recipe.with_related.select_related('author')
        return (
            Recipe.with_related
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
            .annotate(
                is_subscribed=Exists(
                    queryset=Follow.with_related
                    .filter(
                        user=self.request.user,
                        following=OuterRef('pk')
                    )
                )
            )
        )

    def get_following(self) -> User | Http404:
        """Получает подписку."""
        return get_object_or_404(
            User, id=self.kwargs.get('id')
        )

    def get_object(self) -> Follow | Http404:
        """Получает объект связанной модели подписки."""
        return get_object_or_404(
            Follow.objects,
            user=self.request.user,
            following=self.get_following()
        )
