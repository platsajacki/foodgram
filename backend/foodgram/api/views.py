from datetime import date
from io import BytesIO

from django.db.models import QuerySet, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
from .mixins import GetNonePaginatorAllowAny, UserRecipeViewSet
from .permissions import IsAuthor
from .serializers import (
    UserCustomSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    ShoppingCardSerializer, FavouriteRecipeSerializer,
    FollowSerializer
)
from .validators import valide_follow_exists
from .utils import get_xls_shopping_cart
from recipes.models import Tag, Ingredient, Recipe
from users.models import User, ShoppingCard, FavouriteRecipe, Follow


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


class ShoppingCardViewSet(UserRecipeViewSet, ModelViewSet):
    """Представление, отвечающее за работу с корзиной покупок."""
    queryset = ShoppingCard.objects.all()
    serializer_class = ShoppingCardSerializer
    http_method_names = ['get', 'post', 'delete']

    def download_shopping_cart(self, request: Request):
        """
        Метод для скачивания списка покупок
        в формате Excel (XLS) при GET запросе.
        """
        ingredients: QuerySet = (
            ShoppingCard.objects
            .filter(user=request.user)
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
        buffer: BytesIO = get_xls_shopping_cart(ingredients)
        today: date = timezone.now().date()
        return FileResponse(buffer, filename=f'Список покупок_{today}.xls')


class FavouriteRecipeViewSet(UserRecipeViewSet, ModelViewSet):
    """Представление, отвечающее за работу с избранным."""
    queryset = FavouriteRecipe.objects.all()
    serializer_class = FavouriteRecipeSerializer
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
            Follow.objects
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
        try:
            return (
                Follow.objects
                .get(
                    user=self.request.user,
                    following=self.get_following()
                )
            )
        except Follow.DoesNotExist:
            return None

    def perform_destroy(
            self, instance: Follow
    ) -> None | ValidationError:
        """Удаляет объект."""
        valide_follow_exists(instance)
        instance.delete()
