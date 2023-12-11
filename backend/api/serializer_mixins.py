from drf_extra_fields.fields import Base64ImageField

from rest_framework import serializers

from users.models import User, Follow


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
        У объекта должно быть поле 'follower', в котором содержится
        список с моделью подписки, он будет пуcтым,
        если пользователи не связаны.
        Если запрошиваем свои подписки, то в любом случае будет True.
        """
        current_user: User = self.context['request'].user
        if current_user.is_anonymous:
            return False
        if self.Meta.model == Follow:
            return True
        return bool(obj.follower)
