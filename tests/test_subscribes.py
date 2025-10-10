import pytest
from rest_framework import status


@pytest.mark.django_db
def test_subscribe_user(auth_client, another_user, user):
    """Тестируем подписку на пользователя"""
    response = auth_client.post(f'/api/users/{user.id}/subscribe/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'Ошибка'
    )

    response = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == status.HTTP_201_CREATED

    response = auth_client.delete(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == status.HTTP_201_CREATED

    response = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST, (
        'При попытке повторно подписаться на пользователя должен падать '
        f'статус-код {status.HTTP_400_BAD_REQUEST}'
    )
