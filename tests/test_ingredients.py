from http import HTTPStatus

import pytest
from recipes.models import Ingredient


@pytest.mark.django_db
class TestIngredients:
    INGREDIENTS_LIST_URL = '/api/ingredients/'
    INGREDIENTS_SEARCH_URL = '/api/ingredients/?name=яй'

    def test_list_ingredients(self, no_auth_client, auth_client, ingredient):
        response = no_auth_client.get(self.INGREDIENTS_LIST_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = auth_client.get(self.INGREDIENTS_LIST_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

    def test_filter_ingredients(self, no_auth_client, auth_client, ingredient):
        response = no_auth_client.get(self.INGREDIENTS_SEARCH_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = auth_client.get(self.INGREDIENTS_SEARCH_URL)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

    def test_create_ingredients(self, no_auth_client, auth_client, ingredient):
        data = {
            'name': 'Совершенно невнятный ингредиент',
            'measurement_unit': 'гр'
        }
        response = no_auth_client.post(self.INGREDIENTS_LIST_URL, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос неавторизованного пользователя на добавление ингредиента'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Ingredient.objects.filter(name=data['name']).exists(), (
            'POST запрос неавторизованного пользователя не должен создавать '
            'ингредиент в БД'
        )

        response = auth_client.post(self.INGREDIENTS_LIST_URL, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос авторизованного пользователя на добавление ингредиента'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Ingredient.objects.filter(name=data['name']).exists(), (
            'POST запрос авторизованного пользователя не должен создавать '
            'ингредиент в БД'
        )

    def test_delete_ingredients(self, no_auth_client, auth_client, ingredient,
                                ingredient_url):
        response = no_auth_client.delete(ingredient_url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос неавторизованного пользователя на удаление ингредиента'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert Ingredient.objects.filter(id=ingredient.id).exists(), (
            'DELETE запрос неавторизованного пользователя не должен удалять '
            'ингредиент из БД'
        )

        response = auth_client.delete(ingredient_url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос авторизованного пользователя на удаление ингредиента'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert Ingredient.objects.filter(id=ingredient.id).exists(), (
            'DELETE запрос авторизованного пользователя не должен удалять '
            'ингредиент в БД'
        )

    def test_update_ingredients(self, no_auth_client, auth_client, ingredient,
                                ingredient_url):
        data = {
            'name': 'Хрен',
            'measurement_unit': 'гр'
        }
        response = no_auth_client.put(ingredient_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос неавторизованного пользователя на изменение ингредиента'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Ingredient.objects.filter(name=data['name']), (
            'PUT запрос неавторизованного пользователя на изменение '
            'ингредиента не должен менять изгредиент в БД'
        )

        response = auth_client.put(ingredient_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос авторизованного пользователя на изменение ингредиента'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Ingredient.objects.filter(name=data['name']), (
            'PUT запрос авторизованного пользователя на изменение ингредиента '
            'не должен менять изгредиент в БД'
        )

    def test_partial_update_ingredients(self, no_auth_client, auth_client,
                                        ingredient, ingredient_url):
        data = {
            'measurement_unit': 'гр'
        }
        response = no_auth_client.patch(ingredient_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос неавторизованного пользователя на частичное изменение '
            'ингредиента должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Ingredient.objects.filter(
            measurement_unit=data['measurement_unit']), (
            'PATCH запрос авторизованного пользователя на изменение '
            'ингредиента не должен менять изгредиент в БД'
        )

        response = auth_client.patch(ingredient_url, data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Запрос авторизованного пользователя на частичное изменение '
            'ингредиента должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.METHOD_NOT_ALLOWED}'
        )
        assert not Ingredient.objects.filter(
            measurement_unit=data['measurement_unit']), (
            'PATCH запрос авторизованного пользователя на изменение '
            'ингредиента не должен менять изгредиент в БД'
        )
