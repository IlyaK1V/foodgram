import pytest
from rest_framework import status


@pytest.mark.django_db
def test_add_and_remove_from_cart(auth_client, recipe):
    response = auth_client.post(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code in [
        status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    response = auth_client.delete(f'/api/recipes/{recipe.id}/shopping_cart/')
    assert response.status_code in [
        status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST]


@pytest.mark.django_db
def test_download_shopping_cart(auth_client):
    response = auth_client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code in [
        status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
