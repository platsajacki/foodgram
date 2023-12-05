from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserCustomViewSet, TagViewSet,
    IngredientViewSet, RecipeViewSet,
    ShoppingCartViewSet, FavouriteRecipeViewSet,
    FollowViewSet
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
        ShoppingCartViewSet.as_view(
            {'get': 'download_shopping_cart'}
        ),
        name='download_shopping_cart'
    ),
    path(
        'recipes/<int:id>/shopping_cart/',
        ShoppingCartViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='shopping_cart'
    ),
    path(
        'recipes/<int:id>/favorite/',
        FavouriteRecipeViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='favorite'
    ),
    path(
        'users/subscriptions/',
        FollowViewSet.as_view(
            {'get': 'list'}
        ),
        name='subscriptions'
    ),
    path(
        'users/<int:id>/subscribe/',
        FollowViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='subscriptions-action'
    ),
    path('', include(router.urls)),
]
