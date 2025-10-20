from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
)

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройки админки для пользователей с редактируемым паролем."""
    list_display = (
        'id', 'username', 'email',
        'first_name', 'last_name', 'is_staff',
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('id',)
    empty_value_display = '-пусто-'

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name')}),
        (
            'Права доступа', {
                'fields': (
                    'is_active', 'is_staff',
                    'is_superuser', 'groups', 'user_permissions',
                ),
            },
        ),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None, {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2'),
            },
        ),
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки админки для ингредиентов."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Настройки админки для тегов."""
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug', 'color')
    ordering = ('name',)
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    """Встроенная таблица для ингредиентов в рецепте."""
    model = Recipe.ingredients.through
    extra = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки админки для рецептов."""
    list_display = ('id', 'name', 'author', 'count_favorites')
    search_fields = (
        'name', 'author__username',
        'author__first_name', 'author__last_name', 'author__email',
    )
    list_filter = ('tags',)
    inlines = (IngredientInline,)
    ordering = ('id',)
    empty_value_display = '-пусто-'

    @admin.display(description='В избранном')
    def count_favorites(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorited_by.count()


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    """Админка для количества ингредиентов в рецептах."""
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = (
        'recipe__name',
        'ingredient__name',
        'ingredient__measurement_unit',
    )
    list_filter = ('ingredient__name',)
    ordering = ('recipe',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранных рецептов."""
    list_display = ('id', 'user', 'recipe')
    search_fields = (
        'user__username', 'user__first_name',
        'user__last_name', 'recipe__name',
    )
    ordering = ('id',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка для подписок."""
    list_display = ('id', 'user', 'author')
    search_fields = (
        'user__username', 'user__first_name', 'user__last_name',
        'author__username', 'author__first_name',
        'author__last_name',
    )
    ordering = ('id',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для списка покупок."""
    list_display = ('id', 'user', 'recipe')
    search_fields = (
        'user__username', 'user__first_name',
        'user__last_name', 'recipe__name',
    )
    ordering = ('id',)
    empty_value_display = '-пусто-'
