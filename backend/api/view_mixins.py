from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Recipe
from rest_framework.exceptions import ValidationError

from .validators import valide_user_has_recipe


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

    def get_object(self) -> Model | None:
        """Получает объект связанной модели пользователя."""
        try:
            return self.queryset.model.objects.get(
                user=self.request.user,
                recipe=self.get_recipe()
            )
        except self.queryset.model.DoesNotExist:
            return None

    def perform_destroy(self, instance: Model) -> None | ValidationError:
        """Удаляет объект объект связанной модели пользователя."""
        valide_user_has_recipe(instance)
        instance.delete()
