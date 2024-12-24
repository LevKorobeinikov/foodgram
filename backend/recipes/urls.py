from django.urls import path

from recipes.views import short_url

urlpatterns = [
    path('s/<int:pk>/', short_url, name='short_url'),
]
