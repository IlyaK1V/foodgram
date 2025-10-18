from http import HTTPStatus

import pytest

from recipes.models import Tag


@pytest.mark.django_db
class TestTags:
    """Тестирование тегов"""
    TAG_LIST_URL = '/api/tags/'

    def test_list_detail_tags(self, no_auth_client, auth_client, tag, tag_url):
        """Тестируем просмотр списка тегов"""
        response = no_auth_client.get(self.TAG_LIST_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос незарегистрированного пользователя '
            'к списку тегов должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = auth_client.get(self.TAG_LIST_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя '
            'к списку тегов должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = no_auth_client.get(tag_url)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос незарегистрированного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = auth_client.get(tag_url)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

    def test_create_delete_update_tags(
        self, no_auth_client, auth_client, tag,
        tag_url,
    ):
        """Тестируем создание, обновление и удаление тега"""

        data = {'name': 'Новый тег', 'slug': 'new_tag'}

        response = auth_client.post(self.TAG_LIST_URL, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'POST запрос авторизованного пользователя '
            'к списку тегов должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert len(Tag.objects.all()) == 1, (
            'POST запрос авторизованного пользователя '
            'к списку тегов не создает новый тег в БД'
        )

        response = no_auth_client.post(self.TAG_LIST_URL, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'POST запрос неавторизованного пользователя '
            'к списку тегов должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert len(Tag.objects.all()) == 1, (
            'POST запрос неавторизованного пользователя '
            'к списку тегов не создает новый тег в БД'
        )

        response = auth_client.put(tag_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'PUT запрос авторизованного пользователя '
            'должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Tag.objects.filter(name=data['name']).exists(), (
            'PUT запрос авторизованного пользователя '
            'не изменяет тег в БД'
        )

        response = no_auth_client.put(tag_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'PUT запрос неавторизованного пользователя '
            'должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Tag.objects.filter(name=data['name']).exists(), (
            'PUT запрос неавторизованного пользователя '
            'не изменяет тег в БД'
        )

        response = auth_client.patch(tag_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'PATCH запрос авторизованного пользователя '
            'должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Tag.objects.filter(name=data['name']).exists(), (
            'PATCH запрос авторизованного пользователя '
            'не изменяет тег в БД'
        )

        response = no_auth_client.patch(tag_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'PATCH запрос неавторизованного пользователя '
            'должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Tag.objects.filter(name=data['name']).exists(), (
            'PATCH запрос неавторизованного пользователя '
            'не изменяет тег в БД'
        )

        response = auth_client.delete(tag_url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'DELETE запрос авторизованного пользователя '
            'должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert Tag.objects.filter(id=tag.id).exists(), (
            'DELETE запрос авторизованного пользователя '
            'не удаляет тег в БД'
        )

        response = no_auth_client.delete(tag_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'DELETE запрос неавторизованного пользователя '
            'должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert Tag.objects.filter(id=tag.id).exists(), (
            'DELETE запрос неавторизованного пользователя '
            'не удаляет тег в БД'
        )
