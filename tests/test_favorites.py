from http import HTTPStatus

import pytest
from recipes.models import Favorite


@pytest.mark.django_db
class TestFavorites:
    """Тестирование рецепта в избранном"""

    def test_authenticated_user_add_and_remove_favorite(
        self,
        auth_client,
        user,
        recipe,
        recipe_favorite_url,
    ):
        response = auth_client.post(recipe_favorite_url)
        assert response.status_code == HTTPStatus.CREATED, (
            'Запрос авторизованного пользователя на добавление рецепта в '
            'избранное должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.CREATED}'
        )
        assert Favorite.objects.filter(user=user, recipe=recipe).exists(), (
            'После POST-запроса в избранном должна появиться запись для этого '
            'пользователя и рецепта.'
        )

        response = auth_client.delete(recipe_favorite_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Запрос авторизованного пользователя на удаление рецепта из '
            'избранного должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.NO_CONTENT}'
        )
        assert not Favorite.objects.filter(user=user,
                                           recipe=recipe).exists(), (
            'После DELETE-запроса в избранном не должно быть записи для этого '
            'пользователя и рецепта.'
        )

    def test_not_authenticated_user_add_and_remove_favorite(
        self,
        no_auth_client,
        recipe,
        user,
        another_user,
        recipe_favorite_url,
    ):
        response = no_auth_client.post(recipe_favorite_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос анонимного пользователя на добавление рецепта в '
            'избранное должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert not Favorite.objects.filter(user=user,
                                           recipe=recipe).exists(), (
            'После POST запроса неавторизованного пользователя в избранном не '
            f'должно быть записи для пользователя {user} и рецепта.'
        )
        assert not Favorite.objects.filter(user=another_user,
                                           recipe=recipe).exists(), (
            'После POST запроса неавторизованного пользователя в избранном не '
            f'должно быть записи для пользователя {another_user} и рецепта.'
        )

        response = no_auth_client.delete(recipe_favorite_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос анонимного пользователя на удаление рецепта из '
            'избранного должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert not Favorite.objects.filter(user=user,
                                           recipe=recipe).exists(), (
            'После DELETE запроса неавторизованного пользователя '
            'в избранном не '
            f'должно быть записи для пользователя {user} и рецепта.'
        )
        assert not Favorite.objects.filter(user=another_user,
                                           recipe=recipe).exists(), (
            'После DELETE запроса неавторизованного пользователя '
            'в избранном не '
            f'должно быть записи для пользователя {another_user} и рецепта.'
        )
