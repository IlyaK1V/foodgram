import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, IngredientAmount

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        first_name='Test',
        last_name='User',
        password='testpassword'
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def tag(db):
    return Tag.objects.create(name='Завтрак', slug='breakfast')


@pytest.fixture
def ingredient(db):
    return Ingredient.objects.create(name='Яйцо', measurement_unit='шт.')


@pytest.fixture
def recipe(user, tag, ingredient):
    """Создаёт тестовый рецепт с ингредиентом и тегом."""
    recipe = Recipe.objects.create(
        author=user,
        name='Омлет',
        text='Смешайте яйца, обжарьте на сковороде.',
        cooking_time=10,
        image='recipes/test.png'
    )
    recipe.tags.add(tag)
    IngredientAmount.objects.create(
        recipe=recipe, ingredient=ingredient, amount=2)
    return recipe


@pytest.fixture
def another_user(db):
    """Создаёт второго пользователя (для подписок и т.п.)."""
    return User.objects.create_user(
        username='chef',
        email='chef@example.com',
        first_name='Another',
        last_name='TestUser',
        password='chefpass123'
    )


@pytest.fixture
def auth_client_another(another_user):
    """Аутентифицированный клиент второго пользователя."""
    client = APIClient()
    client.force_authenticate(user=another_user)
    return client
