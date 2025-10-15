from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from drf_extra_fields.fields import Base64ImageField
from recipes.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)
from recipes.validators import (CustomUniqueValidator, validate_recipe,
                                validate_username)
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].validators = [
            CustomUniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(EMAIL_MAX_LENGTH),
        ]
        self.fields['username'].validators = [
            CustomUniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(USERNAME_MAX_LENGTH),
            validate_username,
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


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


class IngredientWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    amount = serializers.IntegerField()

    class Meta:
        fields = ('id', 'name', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    image = serializers.ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

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
        data['request'] = self.context.get('request')
        return validate_recipe(data)

    def validate_ingredients_exist(self, ingredients_data):
        """Проверяет, что все ингредиенты существуют."""
        for item in ingredients_data:
            ingredient_id = item.get('id')
            if not ingredient_id:
                raise serializers.ValidationError({
                    'ingredients': 'Каждый ингредиент должен содержать '
                    'поле "id".'
                })
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError({
                    'ingredients': f'Ингредиент с id={ingredient_id} '
                    'не найден.'
                })

    def to_representation(self, instance):
        """
        После создания/обновления возвращаем полное представление рецепта.
        """
        return RecipeListSerializer(instance, context=self.context).data

    def add_ingredients(self, ingredients_data, recipe):
        """Добавить ингредиенты к рецепту (только если они существуют)."""
        for item in ingredients_data:
            ingredient_id = item.get('id')
            amount = item.get('amount')

            if not ingredient_id:
                raise serializers.ValidationError(
                    "Каждый ингредиент должен содержать поле 'id'."
                )
            if amount is None:
                raise serializers.ValidationError(
                    "Каждый ингредиент должен содержать поле 'amount'."
                )

            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError(
                    f"Ингредиент с id={ingredient_id} не найден."
                )

            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data):
        """Создание рецепта с ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        self.validate_ingredients_exist(ingredients_data)
        tags = validated_data.pop('tags')

        validated_data.pop('request', None)

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновление рецепта без создания изображения, если не передано новое.
        """
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        image = validated_data.pop('image', None)

        if image:
            instance.image = image

        # Обновляем теги
        if tags:
            instance.tags.set(tags)

        # Обновляем ингредиенты (очищаем и добавляем заново)
        if ingredients_data:
            instance.ingredient_amounts.all().delete()
            self.add_ingredients(ingredients_data, instance)

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


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
