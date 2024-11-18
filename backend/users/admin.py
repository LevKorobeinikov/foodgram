from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, MyUser


@admin.register(MyUser)
class MyUserAdmin(UserAdmin):
    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'first_name')
    empty_value_display = '-empty-'


@admin.register(Follow)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user', 'author')
    empty_value_display = '-empty-'
