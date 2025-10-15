import pytest
from recipes.models import Ingredient


@pytest.fixture
def ingredient(db):
    return Ingredient.objects.create(name='Яйцо', measurement_unit='шт.')


@pytest.fixture
def ingredient_url(ingredient):
    return f'/api/ingredients/{ingredient.id}/'
