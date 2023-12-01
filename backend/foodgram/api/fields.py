import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


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
        super().to_internal_value(data)
