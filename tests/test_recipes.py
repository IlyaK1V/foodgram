from http import HTTPStatus

import pytest
from recipes.models import Recipe


@pytest.mark.django_db
class TestRecipes:
    RECIPES_LIST_URL = '/api/recipes/'

    def test_get_recipes_list(self, no_auth_client, auth_client, recipe,
                              recipe_get_link_url):
        response = no_auth_client.get('/api/recipes/')
        assert response.status_code == HTTPStatus.OK, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = auth_client.get(recipe_get_link_url)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

    def test_get_short_link(self, no_auth_client, auth_client, recipe,
                            recipe_get_link_url):
        response = no_auth_client.get(recipe_get_link_url)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос неавторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

        response = auth_client.get(recipe_get_link_url)
        assert response.status_code == HTTPStatus.OK, (
            'Запрос авторизованного пользователя должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )

    def test_create_recipe(self, auth_client, no_auth_client, tag, ingredient):
        data = {
            'ingredients': [{'id': ingredient.id, 'amount': 2}],
            'tags': [tag.id],
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg'
            'MAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4'
            'bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
            'name': 'Омлет с сыром',
            'text': 'Просто вкусно',
            'cooking_time': 5
        }

        response = no_auth_client.post(
            self.RECIPES_LIST_URL, data=data, format='json')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя на создание рецепта'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert not Recipe.objects.filter(name=data['name']).exists(), (
            'Запрос неавторизованного пользователя на создание рецепта '
            'не должен создать рецепт в БД'
        )

        response = auth_client.post(self.RECIPES_LIST_URL, data=data,
                                    format='json')
        assert response.status_code == HTTPStatus.CREATED, (
            'Запрос авторизованного пользователя на создание рецепта'
            ' должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.CREATED}'
        )
        assert Recipe.objects.filter(name=data['name']).exists(), (
            'Запрос авторизованного пользователя на создание рецепта '
            'должен создать рецепт в БД'
        )

    def test_create_recipe_with_non_existing_ingredient(
        self,
        auth_client,
        no_auth_client,
        tag,
        ingredient
    ):
        data = {
            "ingredients": [{"id": 99999, "amount": 25}],
            "tags": [tag.id],
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg"
            "MAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4"
            "bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
            "name": "Рецепт с несуществующим ингредиентом",
            "text": "Админ, добавь ингредиент!",
            "cooking_time": 15
        }

        response = auth_client.post(self.RECIPES_LIST_URL, data=data,
                                    format='json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Запрос авторизованного пользователя на создание рецепта '
            'с несуществующим ингредиентом должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        assert not Recipe.objects.filter(name=data['name']).exists(), (
            'Запрос авторизованного пользователя на создание рецепта '
            'с несуществующим ингредиентом не должен создать рецепт в БД'
        )

    def test_delete_recipe(self, auth_client, no_auth_client, recipe,
                           recipe_url):
        response = no_auth_client.delete(recipe_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя на удаление '
            'рецепта должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert Recipe.objects.filter(id=recipe.id).exists(), (
            'Запрос неавторизованного пользователя на создание рецепта '
            'не должен удалить рецепт из БД'
        )

        response = auth_client.delete(recipe_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Запрос авторизованного пользователя на удаление '
            'рецепта должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.NO_CONTENT}'
        )
        assert not Recipe.objects.filter(id=recipe.id).exists(), (
            'Запрос авторизованного пользователя на создание рецепта '
            'должен удалить рецепт из БД'
        )

    def test_update_recipe(
        self,
        auth_client,
        no_auth_client,
        auth_client_another,
        recipe,
        recipe_url,
        ingredient,
        tag,
    ):
        data = {
            'ingredients': [{'id': ingredient.id, 'amount': 2}],
            'tags': [tag.id],
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAg'
            'MAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4'
            'bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==',
            'name': 'Омлет с сыром',
            'text': 'Просто вкусно',
            'cooking_time': 5,
        }

        response = auth_client_another.patch(recipe_url, data, format='json')
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Запрос авторизованного пользователя на изменение '
            'рецепта должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.FORBIDDEN}'
        )
        assert not Recipe.objects.filter(name=data['name']).exists(), (
            'Запрос авторизованного пользователя на изменение рецепта '
            'не должен изменить рецепт в БД'
        )

        response = no_auth_client.patch(recipe_url, data, format='json')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя на изменение '
            'рецепта должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert not Recipe.objects.filter(name=data['name']).exists(), (
            'Запрос неавторизованного пользователя на изменение рецепта '
            'не должен изменить рецепт в БД'
        )

        response = auth_client.patch(recipe_url, data, format='json')
        assert response.status_code == HTTPStatus.OK, (
            'Запрос автора пользователя на изменение '
            'рецепта должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.OK}'
        )
        assert Recipe.objects.filter(name=data['name']).exists(), (
            'Запрос автора рецепта на изменение рецепта '
            'должен изменить рецепт в БД'
        )
