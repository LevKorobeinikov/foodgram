from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from recipes.mixins import RecipeCountAdminMixin
from users.models import Follow, ProjectUser


@admin.register(ProjectUser)
class ProjectUserAdmin(RecipeCountAdminMixin, UserAdmin):
    list_display = (
        'username', 'id',
        'email', 'first_name', 'avatar_display',
        'last_name', 'subscribing_count',
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
    def subscribing_count(self, obj):
        return obj.followers.count()


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user', 'author',)
    empty_value_display = '-empty-'
