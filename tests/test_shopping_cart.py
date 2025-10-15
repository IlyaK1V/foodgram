from http import HTTPStatus

import pytest
from recipes.models import ShoppingCart


@pytest.mark.django_db
class TestShoppingCart:
    """Тестируем список покупок"""

    def test_add_and_remove_from_cart(
        self,
        auth_client,
        no_auth_client,
        recipe,
        shopping_cart_url,
        shopping_non_existent_cart_url,
    ):
        response = no_auth_client.post(shopping_cart_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя на добавление рецепта '
            'в корзину должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )

        response = auth_client.post(shopping_cart_url)
        assert response.status_code == HTTPStatus.CREATED, (
            'Запрос авторизованного пользователя на добавление рецепта '
            'в корзину должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.CREATED}'
        )
        assert ShoppingCart.objects.first(), (
            'Запрос авторизованного пользователя на добавление рецепта '
            'в корзину должен создать корзину в БД'
        )

        response = auth_client.post(shopping_non_existent_cart_url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Запрос авторизованного пользователя на добавление '
            'несуществующего рецепта в корзину должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.NOT_FOUND}'
        )
        assert not ShoppingCart.objects.filter(id=999), (
            'Запрос авторизованного пользователя на добавление '
            'несуществующего рецепта в корзину не должен создать корзину в БД'
        )

        response = auth_client.post(shopping_cart_url)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Запрос авторизованного пользователя на повторное добавление '
            'рецепта в корзину должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.BAD_REQUEST}'
        )
        assert ShoppingCart.objects.filter(recipe_id=recipe.id), (
            'Повторный запрос авторизованного пользователя на добавление '
            'существующего рецепта в корзину не должен создать корзину в БД'
        )
        assert len(ShoppingCart.objects.all()) == 1, (
            'Повторный запрос авторизованного пользователя на добавление '
            'существующего рецепта в корзину не должен изменить '
            'колличество корзин в БД'
        )

        response = no_auth_client.delete(shopping_cart_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Запрос неавторизованного пользователя на удаление '
            'рецепта из корзины должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
        )
        assert ShoppingCart.objects.filter(recipe_id=recipe.id), (
            'Запрос неавторизованного пользователя на удаление '
            'существующего рецепта из корзины не должен удалять корзину из БД'
        )

        response = auth_client.delete(shopping_cart_url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Запрос авторизованного пользователя на удаление '
            'рецепта из корзины должен вернуть ответ '
            f'со статус-кодом {HTTPStatus.NO_CONTENT}'
        )
        assert not ShoppingCart.objects.filter(recipe_id=recipe.id), (
            'Запрос авторизованного пользователя на удаление '
            'существующего рецепта из корзины должен удалять корзину из БД'
        )

    def test_download_shopping_cart(self, auth_client, shopping_cart,
                                    download_shopping_cart_url):
        response = auth_client.get(download_shopping_cart_url)
        assert response.status_code == HTTPStatus.OK
