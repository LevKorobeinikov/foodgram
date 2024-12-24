import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from django.core.validators import MinValueValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.constants import (
    INGREDIENT_AMOUNT_MIN, INGREDIENT_AMOUNT_ZERO
)
from recipes.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingList, Tag
)

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_str), name='image.' + ext)
        return super().to_internal_value(data)


class ProjectUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(allow_null=True, required=False)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed', 'avatar')

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.followers.filter(author=author).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        label='Ингредиент'
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                INGREDIENT_AMOUNT_MIN,
                f'Количество продуктов должно быть больше'
                f'{INGREDIENT_AMOUNT_ZERO}.'
            )
        ]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = ProjectUserSerializer()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text',
            'cooking_time',
        )

    def check_user_status(self, obj, model_class):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return model_class.objects.filter(
            recipe=obj,
            user=request.user
        ).exists()

    def get_is_favorited(self, recipe):
        return self.check_user_status(recipe, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self.check_user_status(obj, ShoppingList)


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        label='Теги',
        allow_empty=False,
        validators=[
            UniqueValidator(queryset=Tag.objects.all())
        ]
    )
    ingredients = RecipeIngredientWriteSerializer(
        many=True, label='Ингредиенты'
    )
    image = Base64ImageField(allow_null=True, label='Изображения')

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name',
            'text', 'cooking_time'
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError('Добавьте ингредиент')
        return ingredients

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = [
            RecipeIngredient(
                ingredient=ingredient_data['id'],
                recipe=recipe,
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = super().create({**validated_data, 'author': user})
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        self.validate_ingredients(validated_data.get('ingredients'))
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriberDetailSerializer(ProjectUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta(ProjectUserSerializer.Meta):
        model = User
        fields = ProjectUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = ('fields',)

    def get_recipes(self, subscriber):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            subscriber.author.recipes.all()[:int(
                request.GET.get('recipes_limit', 10**10)
            )],
            many=True,
            context={'request': request}
        ).data
