from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientViewSet, ProjectUserViewSet,
    RecipeViewSet, TagViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', IngredientViewSet, 'ingredients')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('tags', TagViewSet, 'tags')
router.register('users', ProjectUserViewSet, 'users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
