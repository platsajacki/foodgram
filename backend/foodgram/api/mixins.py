from rest_framework.permissions import AllowAny


class GetNonePaginatorAllowAny:
    """
    Предоставляет настройки для представлений, позволяя только метод GET,
    отключая пагинацию и устанавливая разрешения на 'AllowAny'.
    """
    pagination_class = None
    http_method_names = ['get',]
    permission_classes = [AllowAny,]
