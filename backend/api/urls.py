from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet,
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # Основные маршруты API
    path('', include(router.urls)),

    # Аутентификация и управление пользователем
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
