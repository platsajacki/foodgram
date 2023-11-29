from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserCustomViewSet

router = DefaultRouter()
router.register(
    r'users',
    UserCustomViewSet,
    basename='users'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
