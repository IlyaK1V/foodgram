from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

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
