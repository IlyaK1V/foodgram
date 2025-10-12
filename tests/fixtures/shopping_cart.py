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
