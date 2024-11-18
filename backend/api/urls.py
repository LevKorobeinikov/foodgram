from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views import (
    CustomUserViewSet, IngredientViewSet,
    RecipeViewSet, TagViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('tags', TagViewSet, 'tags')
router.register('users', CustomUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('docs/', TemplateView.as_view(
        template_name='docs/redoc.html'),
        name='redoc'
    ),
    path('auth/', include('djoser.urls.authtoken')),
]
