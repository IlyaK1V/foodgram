import django_filters
from django_filters.rest_framework import FilterSet
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по избранному."""
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по корзине."""
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset.exclude(shopping_cart__user=user)
