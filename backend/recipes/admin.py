from django.contrib import admin

from foodgram.constants import INLINE_EXTRA
from recipes.models import Ingredient, Recipe, Tag


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = INLINE_EXTRA


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = INLINE_EXTRA


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'author',)
    search_fields = ('name', 'author',)
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-empty-'
