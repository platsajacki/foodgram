from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .fields import Base64ImageField
from .validators import valide_user_has_recipe
from users.models import User, Follow


class GetNonePaginatorAllowAny:
    """
    Предоставляет настройки для представлений, позволяя только метод GET,
    отключая пагинацию и устанавливая разрешения на 'AllowAny'.
    """
    pagination_class = None
    http_method_names = ['get',]
    permission_classes = [AllowAny,]


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


class UserRecipeFieldsSet(serializers.Serializer):
    """
    Миксин сериализатора для извлечения
    ID, название, изображение и время приготовления экземпляра рецепта.
    """
    id = serializers.IntegerField(
        source='recipe.id', read_only=True
    )
    name = serializers.CharField(
        source='recipe.name', read_only=True
    )
    image = Base64ImageField(
        source='recipe.image', read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )


class SubscribedMethodField(serializers.Serializer):
    """
    Миксин сериализатора с методом,
    отвечающим за получение поля 'is_subscribed'.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def _get_is_subscribed(self, obj: User) -> bool:
        """
        Определяет подаписан ли запрашиваемый пользователь на текущего.
        В случае, если пользователь анонимный, возвращается 'False'.
        """
        current_user: User = self.context['request'].user
        if isinstance(current_user, AnonymousUser):
            return False
        return (
            Follow.objects
            .filter(
                user=current_user,
                following=obj
            ).exists()
        )
