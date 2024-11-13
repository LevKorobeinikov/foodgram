from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet, IngredientsViewSet, RecipeViewSet,
    TagsViewSet
)

app_name = 'api'
router_v1 = DefaultRouter()
router_v1.register('tags', TagsViewSet, 'tags')
router_v1.register('ingredients', IngredientsViewSet, 'ingredients')
router_v1.register('recipes', RecipeViewSet, 'recipes')
router_v1.register('users', CustomUserViewSet, 'users')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('docs/', TemplateView.as_view(
        template_name='docs/redoc.html'), name='redoc'
    ),
    path('auth/', include('djoser.urls.authtoken')),
]
