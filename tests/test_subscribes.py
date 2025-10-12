from http import HTTPStatus
import pytest

from recipes.models import Follow


@pytest.mark.django_db
def test_add_delete_subscribe_user(auth_client, auth_client_another,
                                   another_user, user):
    """Тестируем подписку на пользователя"""
    response = auth_client.post(f'/api/users/{user.id}/subscribe/')
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        'Запрос зарегистрированного пользователя на создание подписки '
        'подписки на самого себя должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.BAD_REQUEST}'
    )
    assert not Follow.objects.filter(user=user, author=user).exists(), (
        'Подписка на самого себя не должна сохраняться в БД.'
    )

    response = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == HTTPStatus.CREATED, (
        'Запрос зарегистрированного пользователя на создание подписки '
        'подписки на другого пользователя должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.CREATED}'
    )
    assert Follow.objects.filter(user=user, author=another_user).exists(), (
        'После успешной подписки запись должна появиться в БД.'
    )

    response = auth_client.post(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        'При попытке повторно подписаться на пользователя должен падать '
        f'статус-код {HTTPStatus.BAD_REQUEST}'
    )
    assert len(Follow.objects.all()) == 1, (
        'В БД должна остаться ровно одна запись подписки между пользователем '
        'и автором.'
    )
    assert Follow.objects.filter(
        user=user, author=another_user).count() == 1, (
        'При попытке повторно подписаться на пользователя не создается '
        'идентичная запись в БД'
    )

    response = auth_client_another.post(f'/api/users/{user.id}/subscribe/')
    assert response.status_code == HTTPStatus.CREATED, (
        'Запрос зарегистрированного пользователя на создание подписки '
        'друг на друга должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.CREATED}'
    )
    assert Follow.objects.filter(user=another_user, author=user).exists(), (
        'После успешной подписки друг на друга запись должна появиться в БД.'
    )

    response = auth_client.delete(f'/api/users/{another_user.id}/subscribe/')
    assert response.status_code == HTTPStatus.NO_CONTENT, (
        'Запрос зарегистрированного пользователя на удаление подписки '
        'должен вернуться ответ '
        f'со статус-кодом {HTTPStatus.NO_CONTENT}'
    )
    assert not Follow.objects.filter(
        user=user, author=another_user).exists(), (
        'После удаления подписки запись должна появиться в БД.'
    )

    response = auth_client_another.delete(f'/api/users/{user.id}/subscribe/')
    assert response.status_code == HTTPStatus.NO_CONTENT, (
        'Запрос зарегистрированного пользователя на удаление подписки '
        'друг на друга должен вернуться ответ '
        f'со статус-кодом {HTTPStatus.NO_CONTENT}'
    )
    assert not Follow.objects.filter(
        user=another_user, author=user).exists(), (
        'После удаления подписки друг на друга запись должна появиться в БД.'
    )
