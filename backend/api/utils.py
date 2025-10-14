from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from .serializers import RecipeMinifiedSerializer
from recipes.models import Recipe


def toggle_relation(
        request,
        pk=None,
        recipe_model=Recipe,
        model=None,
        existing_error_message=None,
        non_existing_error_message=None,
):

    recipe = get_object_or_404(recipe_model, pk=pk)
    if request.method == 'POST':
        # Проверяем — уже добавлен ли рецепт
        if model.objects.filter(user=request.user,
                                recipe=recipe).exists():
            return Response(
                existing_error_message,
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    item = model.objects.filter(
        user=request.user, recipe=recipe)
    if not item.exists():
        return Response(
            non_existing_error_message,
            status=status.HTTP_400_BAD_REQUEST
        )
    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
