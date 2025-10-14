import django_filters
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe


class CustomBooleanFilter(filters.BooleanFilter):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = BooleanWidget
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        # value придется преобразовать в True/False
        # Так как стандартный BooleanWidget не работает с '1'/'0'
        # нам нужно сделать это самостоятельно
        if value is None:
            return qs
        if isinstance(value, str):
            value = value.lower() in ['true', '1']

        if value:
            return self.method(qs, self.field_name, True)
        return self.method(qs, self.field_name, False)


class RecipeFilter(filters.FilterSet):
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = CustomBooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = CustomBooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        # value здесь будет уже булевым True или False
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset.exclude(favorited_by__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        # value здесь будет уже булевым True или False
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()
        if value:
            return queryset.filter(shopping_cart__user=user)
        return queryset.exclude(shopping_cart__user=user)
