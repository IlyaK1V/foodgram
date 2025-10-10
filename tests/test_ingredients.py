import pytest
from rest_framework import status


@pytest.mark.django_db
def test_list_ingredients(api_client, ingredient):
    response = api_client.get('/api/ingredients/')
    assert response.status_code == status.HTTP_200_OK
    assert any(i['name'] == ingredient.name for i in response.data)


@pytest.mark.django_db
def test_filter_ingredients(api_client, ingredient):
    response = api_client.get('/api/ingredients/?name=яй')
    assert response.status_code == status.HTTP_200_OK
