import pytest
from rest_framework import status


@pytest.mark.django_db
def test_add_and_remove_favorite(auth_client, recipe):
    response = auth_client.post(f'/api/recipes/{recipe.id}/favorite/')
    assert response.status_code in [
        status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    response = auth_client.delete(f'/api/recipes/{recipe.id}/favorite/')
    assert response.status_code in [
        status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST]
