from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from api.filters import CookingTimeFilter
from recipes.constants import INLINE_EXTRA
from recipes.mixins import RecipeCountAdminMixin
from recipes.models import (Follow, Ingredient, ProjectUser, Recipe,
                            RecipeIngredient, Tag)


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
    def avatar_display(self, obj):
        if obj.avatar:
            return (
                f'<img src="{obj.avatar.url}"'
                f'width: 50px; height: 50px;'
                f'border-radius: 50%;" alt="Avatar" />'
            )
        return '-empty-'

    @admin.display(description='Количество подписчиков')
    def subscriber_count(self, obj):
        return obj.authors.count()

    @admin.display(description='Количество подписок')
    def subscribing_count(self, obj):
        return obj.followers.count()


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
    def tags_display(self, obj):
        return ', '.join(
            f'<span style="color: #007bff;">'
            f'{tag.name}</span>' for tag in obj.tags.all()
        )

    @admin.display(description='Количество в избранном')
    def favorite_count(self, obj):
        return obj.favorite.count()

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_display(self, obj):
        return '<br>'.join(
            f'<span>{ingredient.ingredient.name} —'
            f'{ingredient.amount}'
            f'{ingredient.ingredient.measurement_unit}</span>'
            for ingredient in obj.recipe_ingredients.all()
        )

    @admin.display(description='Картинка')
    @mark_safe
    def image_display(self, obj):
        if obj.image:
            return (
                f'<img src="{obj.image.url}"'
                f'style="width: 100px; height: auto;" alt="Recipe Image"/>'
            )
        return '-empty-'


@admin.register(Tag)
class TagAdmin(RecipeCountAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipe_count',)
    search_fields = ('name', 'slug',)
    empty_value_display = '-empty-'


admin.site.unregister(Group)
