import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import RecipeIngredient


class Base64ImageField(serializers.ImageField):
    """Поле сериализатора для обработки изображений в формате Base64."""
    def to_internal_value(self, data):
        """
        Преобразует предоставленные данные изображения
        в формате Base64 в объект файла изображения.
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientRecipeWriteField(serializers.ModelSerializer):
    """Сериализатор для записи данных о ингредиентах рецепта."""
    id = serializers.IntegerField(source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)
        write_only_fields = ('id', 'amount',)
