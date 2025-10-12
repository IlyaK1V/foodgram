import pytest

from recipes.models import Ingredient


@pytest.fixture
def ingredient(db):
    return Ingredient.objects.create(name='Яйцо', measurement_unit='шт.')
