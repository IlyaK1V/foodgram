from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .constants import FORBIDDEN_USERNAMES


class CustomUniqueValidator(UniqueValidator):
    """Переопределённый UniqueValidator с кастомным сообщением об ошибке."""

    def __call__(self, field, serializer_field):
        if self.queryset.filter(
                **{serializer_field.field_name: field}).exists():
            raise serializers.ValidationError(
                (f'Пользователь с {serializer_field.field_name} {field}'
                 ' уже зарегистрирован.')
            )


def validate_username(username: str) -> str:
    """Валидация имени пользователя."""

    UnicodeUsernameValidator()(username)

    if username in FORBIDDEN_USERNAMES:
        raise ValidationError(f'username не может быть {username}')

    return username


def validate_recipe(data):
    """Проверяет уникальность тегов и ингредиентов в рецепте."""
    ingredients = data.get('ingredients', [])
    tags = data.get('tags', [])
    image = data.get('image')
    request = data.get('request')
    method = getattr(request, 'method', None)

    if method == 'POST' and not image:
        raise serializers.ValidationError({
            'image': ['Нужно добавить изображение рецепта.']
        })
    if method == 'PATCH' and image in [None, '']:
        raise serializers.ValidationError({
            'image': ['Нельзя отправлять пустое поле изображения.']
        })

    # Проверка, указан что хотя бы один ингредиент
    if not ingredients:
        raise serializers.ValidationError(
            {'ingredients': 'Нужно добавить хотя бы один ингредиент.'}
        )

    # Проверка, что указан хотя бы один тег
    if not tags:
        raise serializers.ValidationError(
            {'tags': 'Нужно указать хотя бы один тег.'}
        )

    for ingredient in ingredients:
        if ingredient.get('amount') < 1:
            raise serializers.ValidationError(
                {'ingredients': ('Колличество любого ингредиента '
                                 'не может быть меньше 1')}
            )

    # Проверка на дубли ингредиентов
    ingredient_ids = [item.get('id') for item in ingredients]
    if len(ingredient_ids) != len(set(ingredient_ids)):
        raise serializers.ValidationError(
            {'ingredients': 'Ингредиенты не должны повторяться.'}
        )

    # Проверка на дубли тегов
    tag_ids = [tag.id for tag in tags]
    if len(tag_ids) != len(set(tag_ids)):
        raise serializers.ValidationError(
            {'tags': 'Теги не должны повторяться.'}
        )

    return data
