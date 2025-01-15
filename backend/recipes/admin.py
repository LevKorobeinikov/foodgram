from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from api.filters import CookingTimeFilter
from recipes.constants import INLINE_EXTRA
from recipes.models import (
    Favorite, Follow, Ingredient, ProjectUser, Recipe,
    RecipeIngredient, ShoppingList, Tag
)


class RecipeCountAdminMixin:
    @admin.display(description='Количество рецептов')
    def recipe_count(self, obj):
        return obj.recipes.count()


class RecipeIngredientsInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = INLINE_EXTRA


@admin.register(ProjectUser)
class ProjectUserAdmin(RecipeCountAdminMixin, UserAdmin):
    list_display = (
        'username', 'id',
        'email', 'first_name', 'avatar_display',
        'last_name', 'subscriber_count', 'subscribing_count',
        'recipe_count',
    )
    list_filter = ('email', 'first_name')
    search_fields = ('email', 'username',)
    empty_value_display = '-empty-'

    @mark_safe
    @admin.display(description='Аватар')
    def avatar_display(self, user):
        return (
            f'<img src="{user.avatar.url}"'
            f'width: 10px; height: 10px;'
            f'border-radius: 50%;" alt="Avatar" />'
            if user.avatar else ''
        )

    @admin.display(description='Подписчики')
    def subscriber_count(self, user):
        return user.authors.count()

    @admin.display(description='Подписки')
    def subscribing_count(self, user):
        return user.followers.count()


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user', 'author',)
    empty_value_display = '-empty-'


@admin.register(Ingredient)
class IngredientAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'measurement_unit', 'recipe_count',
    )
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-empty-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name',
        'author', 'cooking_time',
        'tags_display', 'favorite_count',
        'ingredients_display', 'image_display'
    )
    search_fields = ('name', 'author', 'tags',)
    list_filter = ('author', CookingTimeFilter,)
    inlines = (RecipeIngredientsInLine,)
    empty_value_display = '-empty-'

    @admin.display(description='Теги')
    @mark_safe
    def tags_display(self, recipe):
        return '<br>'.join(
            tag.name for tag in recipe.tags.all()
        )

    @admin.display(description='В избранном')
    def favorite_count(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_display(self, obj):
        return '<br>'.join(
            f'{ingredient.ingredient.name} —'
            f'{ingredient.amount}'
            f'{ingredient.ingredient.measurement_unit}'
            for ingredient in obj.recipe_ingredients.all()
        )

    @admin.display(description='Картинка')
    @mark_safe
    def image_display(self, obj):
        return (
            f'<img src="{obj.image.url}"'
            f'style="width: 100px; height: auto;" alt="Recipe Image"/>'
            if obj.image else ''
        )


@admin.register(Tag)
class TagAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipe_count',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-empty-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name',)
    list_filter = ('recipe__name', 'ingredient__name',)
    empty_value_display = '-empty-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    list_filter = ('user__username', 'recipe__name',)
    empty_value_display = '-empty-'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user__username', 'recipe__name',)
    list_filter = ('user__username', 'recipe__name',)
    empty_value_display = '-empty-'


admin.site.unregister(Group)
