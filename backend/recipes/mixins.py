from django.contrib import admin


class RecipeCountAdminMixin:
    @admin.display(description='Количество рецептов')
    def recipe_count(self, obj):
        return obj.recipes.count()
