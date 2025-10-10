import pytest
from rest_framework import status


@pytest.mark.django_db
def test_get_recipes_list(api_client, recipe):
    response = api_client.get('/api/recipes/')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_recipe(auth_client, tag, ingredient):
    data = {
        "ingredients": [{"id": ingredient.id, "amount": 2}],
        "tags": [tag.id],
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAA"
        "BieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACkl"
        "EQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
        "name": "Омлет с сыром",
        "text": "Просто вкусно",
        "cooking_time": 5
    }
    response = auth_client.post('/api/recipes/', data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_get_short_link(api_client, recipe):
    response = api_client.get(f'/api/recipes/{recipe.id}/get-link/')
    assert response.status_code == status.HTTP_200_OK
    assert 'short-link' in response.data
