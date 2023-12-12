from django.db.models import Model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Recipe


class GetNonePaginatorAllowAny:
    """
    Предоставляет настройки для представлений, позволяя только метод GET,
    отключая пагинацию и устанавливая разрешения на 'AllowAny'.
    """
    pagination_class = None
    http_method_names = ['get']
    permission_classes = [AllowAny]


class UserRecipeViewSet:
    """
    Миксин для представлений, связанных с рецептами пользователя.
    Предоставляет общие методы для получения рецепта из URL,
    объекта, сязанного с пользователем и рецептом, и удаления рецепта.
    """
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'id'

    def get_recipe(self) -> Recipe:
        """Получает объект рецепта из URL."""
        return get_object_or_404(
            Recipe, id=self.kwargs.get('id')
        )

    def get_object(self) -> Model | Http404:
        """Получает объект связанной модели пользователя."""
        return get_object_or_404(
            self.queryset.model.objects,
            user=self.request.user,
            recipe=self.get_recipe()
        )
