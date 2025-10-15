from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (EMAIL_MAX_LENGTH, INGRIDIENT_MAX_LENGTH,
                        MEASURMENT_UNIT_MAX_LENGTH, MIN_VALUE,
                        RECIPE_MAX_LENGTH, TAG_MAX_LENGTH, USERNAME_MAX_LENGTH)
from .validators import validate_username


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='электронная почта',
        help_text='Адрес электронной почты',
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=(validate_username, UnicodeUsernameValidator()),
        verbose_name='логин',
        help_text='Имя пользователя',
    )
    first_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='Имя',
        help_text='Имя'
    )
    last_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='Фамилия',
        help_text='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Подписка пользователя на автора."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Tag(models.Model):
    name = models.CharField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Наименование',
    )
    slug = models.SlugField(
        max_length=TAG_MAX_LENGTH,
        unique=True,
        verbose_name='Идентификатор (slug)',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGRIDIENT_MAX_LENGTH,
        verbose_name='Наименование',
    )
    measurement_unit = models.CharField(
        max_length=MEASURMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
    )
    name = models.CharField(
        max_length=RECIPE_MAX_LENGTH,
        verbose_name='Наименование',
    )
    text = models.TextField(
        'Описание',
        help_text='Опишите процесс приготовления',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_VALUE)],
        verbose_name='Время приготовления (в минутах)',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_VALUE)],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        default_related_name = 'ingredient_amounts'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe',
            ),
        ]

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
