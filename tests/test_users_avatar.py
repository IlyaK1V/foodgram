import pytest
from rest_framework import status


@pytest.mark.django_db
def test_upload_avatar(auth_client, tmp_path):
    """Загрузка аватара."""
    img = (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAA"
        "AACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImW"
        "NoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
    )
    response = auth_client.put(
        '/api/users/me/avatar/', data={"avatar": img}, format='json')
    assert response.status_code == status.HTTP_200_OK
