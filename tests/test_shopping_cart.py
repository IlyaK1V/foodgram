from http import HTTPStatus
import pytest

from recipes.models import ShoppingCart


@pytest.mark.django_db
def test_add_and_remove_from_cart(auth_client, no_auth_client, recipe):
    response = no_auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Запрос неавторизованного пользователя на добавление рецепта '
        'в корзину должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
    )

    response = auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code == HTTPStatus.CREATED, (
        'Запрос авторизованного пользователя на добавление рецепта '
        f'в корзину должен вернуть ответ со статус-кодом {HTTPStatus.CREATED}'
    )
    assert ShoppingCart.objects.first(), (
        'Запрос авторизованного пользователя на добавление рецепта '
        'в корзину должен создать корзину в БД'
    )

    not_existing_recepe_id = 999
    response = auth_client.post(
        f'/api/recipes/{not_existing_recepe_id}/shopping_cart/')
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Запрос авторизованного пользователя на добавление '
        'несуществующего рецепта в корзину должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.NOT_FOUND}'
    )
    assert not ShoppingCart.objects.filter(id=not_existing_recepe_id), (
        'Запрос авторизованного пользователя на добавление '
        'несуществующего рецепта в корзину не должен создать корзину в БД'
    )

    response = auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
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

    response = no_auth_client.delete(
        f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Запрос неавторизованного пользователя на удаление '
        'рецепта из корзины должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.UNAUTHORIZED}'
    )
    assert ShoppingCart.objects.filter(recipe_id=recipe.id), (
        'Запрос неавторизованного пользователя на удаление '
        'существующего рецепта из корзины не должен удалять корзину из БД'
    )

    response = auth_client.delete(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code == HTTPStatus.NO_CONTENT, (
        'Запрос авторизованного пользователя на удаление '
        'рецепта из корзины должен вернуть ответ '
        f'со статус-кодом {HTTPStatus.NO_CONTENT}'
    )
    assert not ShoppingCart.objects.filter(recipe_id=recipe.id), (
        'Запрос авторизованного пользователя на удаление '
        'существующего рецепта из корзины должен удалять корзину из БД'
    )


@pytest.mark.django_db
def test_download_shopping_cart(auth_client, shopping_cart):
    response = auth_client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code == HTTPStatus.OK
