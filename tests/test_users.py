from http import HTTPStatus
import pytest


@pytest.mark.django_db
class TestUsers:
    """Тестируем загрузку и получение аватара пользователя"""
    USER_AVATAR_URL = '/api/users/me/avatar/'

    def test_user_upload_delete_avatar(self, auth_client, no_auth_client, user,
                                       another_user, tmp_path):
        """Загрузка и удаление аватара."""
        data = {
            'avatar': (
                'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAAB'
                'ieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4b'
                'AAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
            )
        }
        response = no_auth_client.put(self.USER_AVATAR_URL, data,
                                      format='json')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert not user.avatar, (
            'В БД не должна появится ссылка на аватар пользователя'
        )
        assert not another_user.avatar, (
            'В БД не должна появится ссылка на аватар пользователя'
        )

        response = auth_client.put(self.USER_AVATAR_URL, data,
                                   format='json')
        assert response.status_code == HTTPStatus.OK, (
            'Запрос зарегистрированного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )
        assert user.avatar, (
            'В БД должна появится ссылка на аватар пользователя'
        )

        response = no_auth_client.delete(self.USER_AVATAR_URL)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert user.avatar, (
            'В БД не должна появится ссылка на аватар пользователя'
        )

        response = auth_client.delete(self.USER_AVATAR_URL)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Запрос зарегистрированного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.NO_CONTENT}'
        )
        assert not user.avatar, (
            'В БД должна появится ссылка на аватар пользователя'
        )

    @pytest.mark.django_db
    def test_get_user(self, auth_client, no_auth_client, user, tmp_path,
                      user_me_url):
        """Просмотр пользователя."""
        response = no_auth_client.get(user_me_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )

        response = auth_client.get(user_me_url)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )
