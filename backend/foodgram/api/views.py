from django.db.models import QuerySet
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .mixins import GetNonePaginatorAllowAny
from .serializers import (
    UserCustomSerializer, TagSerializer,
    IngredientSerializer
)
from recipes.models import Tag, Ingredient


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
    """Представление, отвечающее за работу с тэгами."""
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
