import pytest
from recipes.models import ShoppingCart


@pytest.fixture
def shopping_cart(user, recipe):
    """
    Создаёт тестовую запись в списке покупок для пользователя.
    Возвращает объект ShoppingCart.
    """
    cart_item = ShoppingCart.objects.create(user=user, recipe=recipe)
    return cart_item


@pytest.fixture
def shopping_cart_url(recipe):
    return f'/api/recipes/{recipe.id}/shopping_cart/'


@pytest.fixture
def shopping_non_existent_cart_url():
    return '/api/recipes/999/shopping_cart/'


@pytest.fixture
def download_shopping_cart_url():
    return '/api/recipes/download_shopping_cart/'
