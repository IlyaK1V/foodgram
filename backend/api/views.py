import base64

from django.db.models import BooleanField, Exists, OuterRef, Sum, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer, UserCreateSerializer
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    RecipeMinifiedSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserSerializer,
)
from recipes.models import (
    Favorite,
    Follow,
    Ingredient,
    IngredientAmount,
    Recipe,
    ShoppingCart,
    Tag,
    User,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = SearchFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.all().prefetch_related(
            'tags', 'ingredient_amounts__ingredient', 'author'
        )

        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(Favorite.objects.filter(
                    user=user, recipe=OuterRef('pk'))),
                is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                    user=user, recipe=OuterRef('pk'))),
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField()),
            )

        return queryset

    def get_serializer_class(self):
        """Определяем сериализатор в зависимости от действия."""
        mapping = {
            'list': RecipeListSerializer,
            'retrieve': RecipeListSerializer,
            'favorite': RecipeMinifiedSerializer,
            'shopping_cart': RecipeMinifiedSerializer,
            'add_favorite': FavoriteSerializer,
            'add_shopping_cart': ShoppingCartSerializer,
            'create': RecipeCreateSerializer,
            'update': RecipeCreateSerializer,
            'partial_update': RecipeCreateSerializer,
        }
        return mapping.get(self.action, RecipeCreateSerializer)

    def _get_item_or_error(self, model, user, recipe, error_message):
        """Возвращает объект для удаления или ошибку, если его нет."""
        item = model.objects.filter(user=user, recipe=recipe)
        if not item.exists():
            return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
        return item

    def _add_recipe(self, request, recipe, model, serializer_class,
                    existing_error_message):
        """Общий метод для добавления рецепта (в избранное или корзину)."""
        user = request.user

        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(existing_error_message,
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(
            data={'user': user.id, 'recipe': recipe.id},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            RecipeMinifiedSerializer(
                recipe, context={'request': request}).data,
            status=status.HTTP_201_CREATED)

    def _remove_recipe(self, model, recipe, user, non_existing_error_message):
        """Общий метод для удаления рецепта (из избранного или корзины)."""
        item = self._get_item_or_error(
            model, user, recipe, non_existing_error_message)
        if isinstance(item, Response):
            return item
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт без сохранения в БД."""
        recipe = get_object_or_404(Recipe, pk=pk)
        encoded_id = base64.urlsafe_b64encode(
            str(recipe.id).encode()).decode().rstrip('=')
        short_url = request.build_absolute_uri(f'/s/{encoded_id}/')
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    @action(detail=False, url_path='s')
    def short_link_retrieve(self, request, pk=None):
        try:
            # Восстанавливаем ID рецепта
            padded_id = pk + '=' * (-len(pk) % 4)
            decoded_id = base64.urlsafe_b64decode(padded_id.encode()).decode()
            recipe_id = int(decoded_id)
        except (ValueError, base64.binascii.Error):
            return Response(
                {'error': 'Некорректная короткая ссылка.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = RecipeListSerializer(recipe, context={'request': request})
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._add_recipe(
            request,
            recipe,
            Favorite,
            FavoriteSerializer,
            existing_error_message={'errors': (
                'Рецепт уже добавлен в избранное.')},
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._remove_recipe(
            Favorite,
            recipe,
            request.user,
            non_existing_error_message={'errors': 'Рецепта нет в избранном.'},
        )

    @action(detail=True,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._add_recipe(
            request,
            recipe,
            ShoppingCart,
            ShoppingCartSerializer,
            existing_error_message={'errors': 'Рецепт уже в списке покупок.'},
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        return self._remove_recipe(
            ShoppingCart,
            recipe,
            request.user,
            non_existing_error_message={'errors': (
                'Рецепта нет в списке покупок.')},
        )

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                {'error': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ingredients = (
            IngredientAmount.objects
            .filter(recipe__shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        shopping_list = []
        for item in ingredients:
            name = item['ingredient__name']
            unit = item['ingredient__measurement_unit']
            amount = item['total_amount']
            shopping_list.append(f'• {name} — {amount} {unit}')

        content = '\n'.join([
            'Список покупок:',
            '====================',
            *shopping_list,
        ])

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; ' \
            'filename="shopping_list.txt"'
        return response


class UserViewSet(DjoserUserViewSet):
    """ViewSet для пользователей и подписок с оптимизацией под Djoser."""
    queryset = User.objects.all()

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия."""
        mapping = {
            'create': UserCreateSerializer,
            'me': UserSerializer,
            'subscriptions': FollowSerializer,
        }
        return mapping.get(self.action, UserSerializer)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Возвращает текущего пользователя."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def _get_author_or_400(self, id):
        """Возвращает автора или выбрасывает ошибку, если подписка на себя."""
        author = get_object_or_404(User, id=id)
        if self.request.user == author:
            raise ValidationError('Нельзя подписаться на себя.')
        return author

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """Смена пароля."""
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Вывод всех авторов, на которых подписан текущий пользователь."""
        follows = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(
            follows, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Подписка на автора."""
        author = self._get_author_or_400(id)
        if Follow.objects.filter(user=request.user, author=author).exists():
            return Response({'errors': 'Вы уже подписаны.'},
                            status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(user=request.user, author=author)
        serializer = FollowSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def remove_subscribe(self, request, id):
        """Отписка от автора."""
        author = self._get_author_or_400(id)
        follow = Follow.objects.filter(user=request.user, author=author)
        if not follow.exists():
            return Response({'errors': 'Вы не подписаны на этого автора.'},
                            status=status.HTTP_400_BAD_REQUEST)

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put'],
            permission_classes=(IsAuthenticated,), url_path='me/avatar')
    def avatar(self, request):
        user = request.user

        if request.data:
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {'avatar': request.build_absolute_uri(user.avatar.url)},
                status=status.HTTP_200_OK
            )
        return Response({'errors': 'Нельзя передавать пустое поле avatar'},
                        status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def remove_avatar(self, request):
        """Удаление аватара пользователя."""
        if request.user:
            request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
