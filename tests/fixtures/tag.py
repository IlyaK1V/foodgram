import pytest

from recipes.models import Tag


@pytest.fixture
def tag(db):
    return Tag.objects.create(name='Завтрак', slug='breakfast')
