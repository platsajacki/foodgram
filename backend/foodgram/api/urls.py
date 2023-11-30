from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserCustomViewSet, TagViewSet, IngredientViewSet

router = DefaultRouter()
router.register(
    r'users',
    UserCustomViewSet,
    basename='users'
)
router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
