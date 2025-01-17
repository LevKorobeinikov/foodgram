from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarSerializer, IngredientSerializer,
    ProjectUserSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, ShortRecipeSerializer,
    SubscriberDetailSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Follow, Ingredient, Recipe,
    RecipeIngredient, ShoppingList, Tag
)
from api.utils import shopping_list_to_txt

User = get_user_model()


class ProjectUserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = ProjectUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = LimitPagination

    @action(['get'], detail=False, permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ['put'],
        detail=False,
        permission_classes=(IsAuthorOrReadOnly,),
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        serializer = AvatarSerializer(
            instance=request.user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar.mapping.delete
    def delete_avatar(self, request, *args, **kwargs):
        user = self.request.user
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        subscriptions = request.user.followers.all()
        authors = [subscription.author for subscription in subscriptions]
        return self.get_paginated_response(
            SubscriberDetailSerializer(
                self.paginate_queryset(authors),
                many=True,
                context={'request': request}
            ).data
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            raise ValidationError(
                'Вы не можете подписаться или отписаться от себя.'
            )
        if self.request.method != 'POST':
            get_object_or_404(Follow, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        follow_instance, created = Follow.objects.get_or_create(
            author=author, user=user
        )
        if not created:
            raise ValidationError(
                f'Вы уже подписаны на пользователя {author}'
            )
        return Response(SubscriberDetailSerializer(
            author, context={'request': request}
        ).data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Recipe.objects.all()
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'get-link'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[AllowAny],
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        if not Recipe.objects.filter(pk=pk).exists():
            raise ValidationError(f'Рецепт с ID {pk} не найден')
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    reverse('short_url', args=[pk])
                )
            },
            status=status.HTTP_200_OK
        )

    @staticmethod
    def manage_list_item(
        model, pk,
        request, error_message,
        serializer_class=None
    ):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            _, created = model.objects.get_or_create(recipe=recipe, user=user)
            if not created:
                raise ValidationError(f'{error_message}: {recipe.name}')
            return Response(
                serializer_class(recipe, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            get_object_or_404(model, recipe=recipe, user=user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.manage_list_item(
            model=ShoppingList,
            pk=pk,
            request=request,
            error_message=('Рецепт уже есть в списке покупок.'),
            serializer_class=ShortRecipeSerializer,
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppinglists__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(sum=Sum('amount'))
            .order_by('ingredient__name')
        )
        recipes = (
            Recipe.objects.filter(shoppinglists__user=request.user)
            .distinct()
        )
        return FileResponse(
            shopping_list_to_txt(ingredients, recipes),
            content_type='text/plain'
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.manage_list_item(
            model=Favorite,
            pk=pk,
            request=request,
            error_message=('Рецепт уже есть в избранном.'),
            serializer_class=ShortRecipeSerializer
        )
