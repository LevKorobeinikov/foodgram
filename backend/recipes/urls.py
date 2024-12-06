from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import path

from recipes.models import Recipe


def short_url(request, pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise ValidationError(f'Рецепт {pk} не существует.')
    return redirect(f'/recipes/{pk}/')


urlpatterns = [
    path('s/<int:pk>/', short_url, name='short_url'),
]
