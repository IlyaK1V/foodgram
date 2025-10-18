from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import (
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)
from recipes.validators import validate_recipe

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = DjoserUserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        error_messages={
            'does_not_exist': 'Ингредиент с таким id не найден.',
            'incorrect_type': 'Некорректный тип значения для поля id.',
        }
    )
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        max_value=MAX_INGREDIENT_AMOUNT,
        error_messages={
            'min_value': ('Количество ингредиента должно быть '
                          f'не меньше {MIN_INGREDIENT_AMOUNT}.'),
            'max_value': ('Количество ингредиента не может '
                          f'превышать {MAX_INGREDIENT_AMOUNT}.'),
            'invalid': 'Количество ингредиента должно быть целым числом.'
        }
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_amounts',
    )
    image = Base64ImageField(read_only=True)

    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return IngredientInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        error_messages={
            'does_not_exist': 'Тег с таким id не найден.',
            'incorrect_type': 'Некорректный тип значения для поля tags.',
        }
    )
    image = Base64ImageField(required=False, allow_null=True)

    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME,
        error_messages={
            'min_value': ('Время готовки не может быть '
                          f'меньше {MIN_COOKING_TIME} мин.'),
            'max_value': ('Время готовки не может '
                          f'превышать {MAX_COOKING_TIME} мин.'),
            'invalid': 'Время готовки должно быть целым числом.',
        }
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        validators = (validate_recipe,)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Необходимо указать хотя бы один ингредиент.'
            })

        ingredient_ids = [item['id'] for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться.',
            })

        return data

    def _create_ingredient_amounts(self, recipe, ingredients_data):
        """Создаём связь ингредиентов и рецепта одной операцией."""
        ingredient_amounts = [
            IngredientAmount(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(ingredient_amounts)

    @transaction.atomic
    def create(self, validated_data):
        """Создание рецепта с ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context['request'].user

        recipe = super().create({**validated_data, 'author': user})
        recipe.tags.set(tags)
        self._create_ingredient_amounts(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        recipe = super().update(instance, validated_data)

        if tags is not None:
            recipe.tags.set(tags)

        if ingredients_data is not None:
            recipe.ingredient_amounts.all().delete()
            self._create_ingredient_amounts(recipe, ingredients_data)

        return recipe

    def to_representation(self, instance):
        """После создания/обновления возвращаем детализированный рецепт."""
        return RecipeListSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    """Сериализатор для вывода подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Выводим сокращённый список рецептов автора."""
        request = self.context.get('request')
        recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(recipes, many=True,
                                        context={'request': request}).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
