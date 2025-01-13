from django.contrib.admin import SimpleListFilter
from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
        label='Tags'
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, recipes, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return recipes.filter(favorites__user_id=user.id)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        user = (
            self.request.user
            if self.request.user.is_authenticated
            else None
        )
        if value and user:
            return recipes.filter(shoppinglists__user_id=user.id)
        return recipes


class CookingTimeFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_category'

    def lookups(self, request, model_admin):
        cooking_times = Recipe.objects.values_list('cooking_time', flat=True)
        if not cooking_times:
            return []

        sorted_times = sorted(cooking_times)
        self.n = sorted_times[len(sorted_times) // 3]
        self.m = sorted_times[2 * len(sorted_times) // 3]

        quick_count = Recipe.objects.filter(cooking_time__lt=self.n).count()
        medium_count = Recipe.objects.filter(
            cooking_time__gte=self.n,
            cooking_time__lt=self.m).count()
        long_count = Recipe.objects.filter(cooking_time__gte=self.m).count()

        return [
            ('quick', f'быстрее {self.n} мин ({quick_count})'),
            ('medium', f'{self.n}-{self.m} мин ({medium_count})'),
            ('long', f'дольше {self.m} мин ({long_count})'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'quick':
            return queryset.filter(cooking_time__lt=int(self.n))
        elif self.value() == 'medium':
            return queryset.filter(
                cooking_time__gte=int(self.n), cooking_time__lt=int(self.m)
            )
        elif self.value() == 'long':
            return queryset.filter(cooking_time__gte=int(self.m))
        return queryset
