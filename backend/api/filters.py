import django_filters

from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe


class TransformativeBooleanFilter(filters.BooleanFilter):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = BooleanWidget
        super().__init__(*args, **kwargs)

    def filter(self, queryset, value):
        # value придется преобразовать в True/False
        # Так как стандартный BooleanWidget не работает с '1'/'0'
        # нам нужно сделать это самостоятельно
        if value is None:
            return queryset
        if isinstance(value, str):
            value = value.lower() in ('true', '1')

        if value:
            return self.method(queryset, self.field_name, True)
        return self.method(queryset, self.field_name, False)


class RecipeFilter(filters.FilterSet):
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = TransformativeBooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = TransformativeBooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def _boolean_filter(self, queryset, name, value, filter_field):
        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()

        filter_kwargs = {filter_field: user}

        if value:
            return queryset.filter(**filter_kwargs)
        return queryset.exclude(**filter_kwargs)

    def filter_is_favorited(self, queryset, name, value):
        return self._boolean_filter(self, queryset, name, value,
                                    filter_field='favorited_by__user')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self._boolean_filter(self, queryset, name, value,
                                    filter_field='shopping_cart__user')
