from http import HTTPStatus
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthAndRegistration:
    """Тесты для регистрации и аутентификации пользователей."""

    USERS_URL = '/api/users/'
    TOKEN_LOGIN_URL = '/api/auth/token/login/'
    ME_URL = '/api/users/me/'
    SET_PASSWORD_URL = '/api/users/set_password/'

    def test_registration_with_empty_data(self, no_auth_client):
        """Регистрация без данных"""
        response = no_auth_client.post(self.USERS_URL)
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
        response = no_auth_client.post(self.USERS_URL, data=data)
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
        response = no_auth_client.post(self.USERS_URL, data=data)
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
        response = no_auth_client.post(self.USERS_URL, data=data)
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
        response = no_auth_client.post(self.USERS_URL, data=data)
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
        response = no_auth_client.post(self.USERS_URL, data=data)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что если в запросе на регистрацию нового пользователя '
            'не передан `password` - возвращается ответ со '
            f'статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        user = User.objects.filter(email=data['email'])
        assert not user.exists(), (
            'Убедитесь, что пользователь, '
            'содержащий пустые данные, сохраняется в БД'
        )

    def test_registration_with_valid_data(self, no_auth_client):
        """Регистрация с корректными данными."""
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpassword123',
        }
        response = no_auth_client.post(self.USERS_URL, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            'Убедитесь, что запроc на регистрацию нового пользователя, '
            'содержащий корректные данные, возвращает ответ со '
            f'статус-кодом {HTTPStatus.CREATED}'
        )
        user = User.objects.filter(email=data['email'])
        assert user.exists(), (
            'Убедитесь, что пользователь, '
            'содержащий корректные данные, не сохраняется в БД'
        )

    def test_registration_with_duplicate_email_or_username(self,
                                                           no_auth_client):
        """Повторная регистрация с тем же email или username"""
        data = {
            'email': 'sup@example.com',
            'username': 'user1',
            'first_name': 'A',
            'last_name': 'B',
            'password': '12345qwerty',
        }
        no_auth_client.post(self.USERS_URL, data=data)
        user = User.objects.filter(username=data['username'])
        assert user.exists(), (
            'Убедитесь что пользователь с корректными данными создаётся в БД')
        new_username = 'anotheruser'
        response = no_auth_client.post(self.USERS_URL, data={
            **data,
            'username': new_username,
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если при регистрации нового пользователя в запрос передан `email`'
            ' зарегистрированного пользователя - должен вернуться ответ '
            f'со статусом {HTTPStatus.BAD_REQUEST}'
        )
        user = User.objects.filter(username=new_username)
        assert not user.exists(), (
            'Убедитесь, что пользователь, '
            'содержащий существующий email, не сохраняется в БД'
        )
        new_email = 'anotheruser@example.com'
        response = no_auth_client.post(self.USERS_URL, data={
            **data,
            'email': new_email,
        })
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Если при регистрации нового пользователя в запрос передан '
            '`username` зарегистрированного пользователя - должен '
            f'вернуться ответ со статусом {HTTPStatus.BAD_REQUEST}'
        )
        user = User.objects.filter(email=new_email)
        assert not user.exists(), (
            'Убедитесь, что пользователь, '
            'содержащий существующий username данные, не сохраняется в БД'
        )

    def test_login_and_access_me(self, user, no_auth_client):
        """Проверка авторизации и получения данных"""
        login_data = {'email': user.email, 'password': 'testpassword'}
        response = no_auth_client.post(self.TOKEN_LOGIN_URL, data=login_data)
        assert response.status_code == HTTPStatus.OK, (
            'Убедитесь, что при вводе верных логина и пароля при авторизации'
            f'возращается ответ со статусом {HTTPStatus.OK}'
        )
        token = response.data.get('auth_token')
        assert token, 'Ответ должен содержать auth_token'

        no_auth_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = no_auth_client.get(self.ME_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Убедитесь, что при передаче токена'
            f'возращается ответ со статусом {HTTPStatus.OK}'
        )
        assert response.data['email'] == user.email, (
            'Убедитесь, что передан верный токен'
        )

    def test_set_password(self, auth_client):
        """Проверка смены пароля через set_password"""
        data = {
            'new_password': 'newpass12345',
            'current_password': 'testpassword'
        }
        response = auth_client.post(self.SET_PASSWORD_URL, data=data)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Убедитесь, что при смене пароля'
            f'возращается ответ со статусом {HTTPStatus.NO_CONTENT}'
        )

    def test_login_with_invalid_credentials(self, auth_client, user):
        """Логин с неверными данными"""
        data = {'email': 'test@example.com', 'password': 'wrongpass'}
        response = auth_client.post(self.TOKEN_LOGIN_URL, data=data)
        user = User.objects.filter(email=data['email'])
        assert user.exists(), 'Убедитесь что пользователь есть в БД'
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Убедитесь, что при вводе неверного пароля'
            f'возращается ответ со статусом {HTTPStatus.BAD_REQUEST}'
        )

