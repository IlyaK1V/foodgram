import pytest

from recipes.models import IngredientAmount, Recipe


@pytest.fixture
def recipe(user, tag, ingredient):
    """Создаёт тестовый рецепт с ингредиентом и тегом."""
    recipe = Recipe.objects.create(
        author=user,
        name='Омлет',
        text='Смешайте яйца, обжарьте на сковороде.',
        cooking_time=10,
        image='recipes/test.png'
    )
    recipe.tags.add(tag)
    IngredientAmount.objects.create(
        recipe=recipe, ingredient=ingredient, amount=2)
    return recipe


@pytest.fixture
def recipe_url(recipe):
    return f'/api/recipes/{recipe.id}/'


@pytest.fixture
def recipe_favorite_url(recipe):
    return f'/api/recipes/{recipe.id}/favorite/'


@pytest.fixture
def recipe_get_link_url(recipe):
    return f'/api/recipes/{recipe.id}/get-link/'
