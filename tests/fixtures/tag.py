import pytest
from recipes.models import Tag


@pytest.fixture
def tag(db):
    return Tag.objects.create(name='Завтрак', slug='breakfast')


@pytest.fixture
def tag_url(tag):
    return f'/api/tags/{tag.id}/'
