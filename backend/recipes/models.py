from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import (CASCADE, CharField, ForeignKey, ImageField,
                              ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)

from foodgram.constants import (COOKING_TIME_MIN, INGREDIENT_AMOUNT_MIN,
                                INGREDIENT_NAME_MAX_LENGTH,
                                MEASUREMENT_UNIT_MAX_LENGTH,
                                RECIPE_NAME_MAX_LENGTH, TAG_NAME_MAX_LENGTH,
                                TAG_SLUG_MAX_LENGTH)
from users.models import MyUser


class Ingredient(Model):
    name = CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название ингредиента',
        help_text='Введите название ингредиента',
    )
    measurement_unit = CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения',
        help_text='Укажите единицу измерения',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(Model):
    name = CharField(
        max_length=TAG_NAME_MAX_LENGTH,
        verbose_name='Название тега',
        help_text='Введите название тега',
    )
    slug = SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Используйте буквы, цифры и символ подчеркивания.'
            )
        ],
        verbose_name='Слаг тега',
        help_text='Введите уникальный слаг для тега',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(Model):
    name = CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название рецепта',
        help_text='Введите название рецепта',
    )
    text = TextField(
        verbose_name='Описание рецепта',
        help_text='Добавьте описание рецепта',
    )
    ingredients = ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text='Добавьте ингредиенты для рецепта',
    )
    cooking_time = PositiveSmallIntegerField(
        validators=(MinValueValidator(
            COOKING_TIME_MIN,
            f'Не может быть меньше {COOKING_TIME_MIN} минут',
        ),),
        verbose_name='Время приготовления (минуты)',
        help_text='Укажите время приготовления в минутах',
    )
    image = ImageField(
        blank=False,
        verbose_name='Изображение рецепта',
        help_text='Загрузите изображение для рецепта',
        upload_to='media/recipes/',
    )
    author = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = ManyToManyField(
        Tag,
        blank=False,
        through='RecipeTags',
        related_name='recipes',
        verbose_name='Теги рецепта',
        help_text='Добавьте теги для рецепта',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт'
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='ingredient_recipe',
        verbose_name='Ингредиент'
    )
    amount = PositiveSmallIntegerField(
        validators=(MinValueValidator(
            INGREDIENT_AMOUNT_MIN,
            f'Минимальное количество: { INGREDIENT_AMOUNT_MIN}',
        ),),
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_recipe_ingredient',
            ),
        )

    def __str__(self):
        return (
            f'В рецепте "{self.recipe}"'
            f'используется ингредиент "{self.ingredient}"'
        )


class RecipeTags(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='tag_list',
        verbose_name='Рецепт'
    )
    tag = ForeignKey(
        Tag,
        on_delete=CASCADE,
        related_name='tag_recipe',
        verbose_name='Тег'
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'

    def __str__(self):
        return f'Рецепт "{self.recipe}" имеет тег "{self.tag}"'


class Favorite(Model):
    user = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        related_name='favorite',
        verbose_name='Пользователь избранного',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favorite',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        return (
            f'Рецепт "{self.recipe}"'
            f'находится в избранном у пользователя {self.user}'
        )


class ShoppingList(Model):
    user = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"

        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe'
            ),
        )

    def __str__(self):
        return (
            f'Рецепт "{self.recipe}"'
            f'в списке покупок пользователя {self.user}'
        )
