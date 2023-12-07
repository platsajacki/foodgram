from django.db.models import Model
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import View


class IsAuthor(permissions.BasePermission):
    """Автор объекта имеет разрешение на доступ."""
    def has_object_permission(
            self, request: Request, view: View, obj: Model
    ) -> bool:
        """Проверяет разрешение доступа к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and obj.author == request.user
        )
