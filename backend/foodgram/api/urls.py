from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserCustomViewSet, TagViewSet,
    IngredientViewSet, RecipeViewSet,
    ShoppingCardViewSet
)

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
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCardViewSet.as_view(
            {'get': 'download_shopping_cart'}
        ),
        name='download_shopping_cart'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingCardViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='shopping_cart'
    ),
    path('', include(router.urls)),
]
