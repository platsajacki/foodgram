from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import UserCustomSerializer


class UserCustomViewSet(UserViewSet):
    """Представление, отвечающее за работу с пользователями в системе."""
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request: Request) -> Response:
        """Получает информацию о текущем авторизованном пользователе."""
        serializer: UserCustomSerializer = self.get_serializer(request.user)
        return Response(serializer.data)
