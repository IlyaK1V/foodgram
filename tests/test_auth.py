import pytest
from http import HTTPStatus
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthAndRegistration:
    """Тесты для регистрации и аутентификации пользователей."""

    SIGNUP_URL = '/api/users/'
    LOGIN_URL = '/api/auth/token/login/'
    ME_URL = '/api/users/me/'
    SET_PASSWORD_URL = '/api/users/set_password/'

    def test_registration_with_empty_data(self, api_client):
        """Регистрация без данных"""
        response = api_client.post(self.SIGNUP_URL)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что пустой запроc на регистрацию нового пользователя,'
            f' возвращает ответ со статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpassword123',
        }
        response = api_client.post(self.SIGNUP_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что если в запросе на регистрацию нового пользователя '
            'не передан `email` - возвращается ответ со '
            f'статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpassword123',
        }
        response = api_client.post(self.SIGNUP_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что если в запросе на регистрацию нового пользователя '
            'не передан `username` - возвращается ответ со '
            f'статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'last_name': 'User',
            'password': 'strongpassword123',
        }
        response = api_client.post(self.SIGNUP_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что если в запросе на регистрацию нового пользователя '
            'не передан `first_name` - возвращается ответ со '
            f'статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'password': 'strongpassword123',
        }
        response = api_client.post(self.SIGNUP_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что если в запросе на регистрацию нового пользователя '
            'не передан `last_name` - возвращается ответ со '
            f'статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
        }
        response = api_client.post(self.SIGNUP_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что если в запросе на регистрацию нового пользователя '
            'не передан `password` - возвращается ответ со '
            f'статус-кодом {HTTPStatus.BAD_REQUEST}'
        )

    def test_registration_with_valid_data(self, api_client):
        """Регистрация с корректными данными."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpassword123',
        }
        response = api_client.post(self.SIGNUP_URL, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            'Убедитесь, что запроc на регистрацию нового пользователя, '
            'содержащий корректные данные, возвращает ответ со '
            f'статус-кодом {HTTPStatus.CREATED}'
        )
        user = User.objects.filter(email=data['email'])
        assert user.exists(), (
            'Убедитесь, что запроc на регистрацию нового пользователя, '
            'содержащий корректные данные, сохраняется в БД'
        )

    def test_registration_with_duplicate_email_or_username(self, api_client):
        """Повторная регистрация с тем же email"""
        data = {
            'email': 'sup@example.com',
            'username': 'user1',
            'first_name': 'A',
            'last_name': 'B',
            'password': '12345qwerty',
        }
        api_client.post(self.SIGNUP_URL, data=data)
        response = api_client.post(self.SIGNUP_URL, data={
            **data,
            'username': 'anotheruser'
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если при регистрации нового пользователя в запрос передан `email`'
            ' зарегистрированного пользователя - должен вернуться ответ '
            f'со статусом {HTTPStatus.BAD_REQUEST}'
        )
        response = api_client.post(self.SIGNUP_URL, data={
            **data,
            'email': 'anotheruser@example.com'
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если при регистрации нового пользователя в запрос передан '
            '`username` зарегистрированного пользователя - должен '
            f'вернуться ответ со статусом {HTTPStatus.BAD_REQUEST}'
        )

    def test_login_and_access_me(self, user, api_client):
        """Проверка авторизации и получения данных"""
        login_data = {'email': user.email, 'password': 'testpassword'}
        response = api_client.post(self.LOGIN_URL, data=login_data)
        assert response.status_code == HTTPStatus.OK, response.data
        token = response.data.get('auth_token')
        assert token, 'Ответ должен содержать auth_token'

        # Доступ к /me/ с токеном
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = api_client.get(self.ME_URL)
        assert response.status_code == HTTPStatus.OK
        assert response.data['email'] == user.email

    def test_set_password(self, auth_client):
        """Проверка смены пароля через /set_password/."""
        data = {
            'new_password': 'newpass12345',
            'current_password': 'testpassword'
        }
        response = auth_client.post(self.SET_PASSWORD_URL, data=data)
        assert response.status_code == HTTPStatus.NO_CONTENT

    def test_login_with_invalid_credentials(self, api_client):
        """Логин с неверными данными"""
        data = {'email': 'test@example.com', 'password': 'wrongpass'}
        response = api_client.post(self.LOGIN_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST
