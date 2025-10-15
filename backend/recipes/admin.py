from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Favorite, Follow, Ingredient, Recipe, ShoppingCart, Tag

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки админки для пользователей."""
    list_display = ('id', 'username', 'email', 'first_name', 'last_name',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    ordering = ('id',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки админки для ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    ordering = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки админки для тегов."""
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug',)
    ordering = ('name',)
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    """Встроенная таблица для ингредиентов в рецепте."""
    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки админки для рецептов."""
    list_display = ('id', 'name', 'author', 'count_favorites',)
    search_fields = ('name', 'author__username', 'author__email',)
    list_filter = ('tags',)
    inlines = (IngredientInline,)
    ordering = ('id',)
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def count_favorites(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorites.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранных рецептов."""
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    ordering = ('id',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка для подписок."""
    list_display = ('id', 'user', 'author',)
    search_fields = ('user__username', 'author__username',)
    ordering = ('id',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для списка покупок."""
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    ordering = ('id',)
    empty_value_display = '-пусто-'
