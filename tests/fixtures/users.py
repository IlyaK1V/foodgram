import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def no_auth_client():
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


@pytest.fixture
def subscribe_user_url(user):
    return f'/api/users/{user.id}/subscribe/'


@pytest.fixture
def subscribe_another_user_url(another_user):
    return f'/api/users/{another_user.id}/subscribe/'


@pytest.fixture
def user_me_url():
    return '/api/users/me/'
