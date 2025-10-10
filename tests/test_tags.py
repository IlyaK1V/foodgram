import pytest
from rest_framework import status


@pytest.mark.django_db
def test_list_tags(api_client, tag):
    response = api_client.get('/api/tags/')
    assert response.status_code == status.HTTP_200_OK
    assert any(t['name'] == tag.name for t in response.data)
