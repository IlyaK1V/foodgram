import base64
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly)

from .filters import RecipeFilter
from recipes.models import (
    User,
    Tag,
    Ingredient,
    IngredientAmount,
    Recipe,
    Favorite,
    ShoppingCart,
    Follow,
)
from .serializers import (
    FollowSerializer,
    UserSerializer,
    UserCreateSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeCreateSerializer,
)
from .permissions import IsAuthorOrReadOnly
from .utils import toggle_relation


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Ingredient.objects.filter(name__istartswith=name)
        return super().get_queryset()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт без сохранения в БД."""
        recipe = get_object_or_404(Recipe, pk=pk)

        encoded_id = base64.urlsafe_b64encode(
            str(recipe.id).encode()).decode().rstrip('=')

        short_url = request.build_absolute_uri(f'/s/{encoded_id}/')

        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):

        return toggle_relation(
            request=request,
            pk=pk,
            recipe_model=Recipe,
            model=Favorite,
            existing_error_message={
                'errors': 'Рецепт уже добавлен в избранное.'},
            non_existing_error_message={'errors': 'Рецепта нет в избранном.'}
        )

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):

        return toggle_relation(
            request=request,
            pk=pk,
            recipe_model=Recipe,
            model=ShoppingCart,
            existing_error_message={'errors': 'Рецепт уже в списке покупок.'},
            non_existing_error_message={'errors': 'Рецепта нет в списке '
                                        'покупок.'}
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                {'error': 'Список покупок пуст.'},
                status=status.HTTP_400_BAD_REQUEST
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


class UserViewSet(ModelViewSet):
    """ViewSet для пользователей и подписок."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Текущий пользователь."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """Смена пароля (POST /users/set_password/)."""
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'error': 'Укажите старый и новый пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(current_password):
            return Response(
                {'error': 'Неверный текущий пароль.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Вывод всех авторов, на которых подписан текущий пользователь."""
        follows = User.objects.filter(following__user=request.user)
        paginator = Paginator(follows, 10)
        page_number = request.query_params.get('page')
        page = paginator.get_page(page_number)
        serializer = FollowSerializer(
            page, many=True, context={'request': request})
        return Response({
            'count': paginator.count,
            'next': page.next_page_number() if page.has_next() else None,
            'previous': (page.previous_page_number() if page.has_previous()
                         else None),
            'results': serializer.data
        })

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        """Подписка и отписка на автора."""
        author = get_object_or_404(User, id=pk)
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response({'errors': 'Нельзя подписаться на себя.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы уже подписаны.'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # DELETE
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response({'errors': 'Вы не подписаны на этого автора.'},
                            status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'],
            permission_classes=(IsAuthenticated,), url_path='me/avatar')
    def avatar(self, request):
        """Загрузка и удаление аватара пользователя."""
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

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
