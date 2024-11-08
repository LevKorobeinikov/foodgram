from django.core import validators
from django.db.models import (
    CASCADE, SET_NULL, CharField, CheckConstraint,
    DateTimeField, ForeignKey, ImageField,
    ManyToManyField, Model, Q, SlugField,
    SmallIntegerField, TextField, UniqueConstraint
)

from foodgram.constants import COLOR_CHOICES
from users.models import MyUser


class Ingredient(Model):
    """Ингридиенты для рецепта."""

    name = CharField(
        max_length=200,
        verbose_name='Название ингредиента',
    )
    measurement_unit = CharField(
        max_length=24,
        verbose_name='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient',
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
            CheckConstraint(
                check=Q(measurement_unit__length__gt=0),
                name='\n%(app_label)s_%(class)s_measurement_unit is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class Tag(Model):
    """Тэги для рецептов."""

    name = CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
    )
    color = CharField(
        max_length=7,
        unique=True,
        choices=COLOR_CHOICES,
        verbose_name='Цвет',
    )
    slug = SlugField(
        max_length=200,
        unique=True,
        verbose_name='Cлаг тэга',
        db_index=False,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} (цвет: {self.color})'


class Recipe(Model):
    """Модель для рецептов."""

    author = ForeignKey(
        MyUser,
        on_delete=SET_NULL,
        null=True,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = CharField(
        max_length=200,
        verbose_name='Название блюда',
    )
    image = ImageField(
        upload_to='media/recipes/',
        verbose_name='Картинка рецепта',
    )
    text = TextField(
        verbose_name='Описание рецепта',
        max_length=200,
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='recipes.IngredientAmount',
        verbose_name='Ингридиенты',
        related_name='recipes',
    )
    tags = ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = SmallIntegerField(
        default=0,
        verbose_name='Время приготовления',
        validators=(
            validators.MinValueValidator(
                1,
                message='Минимальное время приготовления 1 минута'
            ),
        ),
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
            CheckConstraint(
                check=Q(name__length__gt=0),
                name='\n%(app_label)s_%(class)s_name is empty\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'


class IngredientAmount(Model):
    """Количество ингридиентов в блюде."""

    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        verbose_name='Ингридиент',
        related_name='recipe',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient',
    )
    amount = SmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            validators.MinValueValidator(
                1,
                message='Минимальное количество ингридиентов 1'
            ),
        ),
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Количество ингридиента'
        verbose_name_plural = 'Количество ингридиентов'
        constraints = (
            UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name="\n%(app_label)s_%(class)s ingredient added\n",
            ),
        )

    def __str__(self) -> str:
        return f"{self.amount} {self.ingredient}"


class Favorite(Model):
    """Избранные рецепты."""

    user = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Понравившиеся рецепты',
        related_name='in_favorites',
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True, editable=False
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='\n%(app_label)s_%(class)s recipe is favorite alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'


class Cart(Model):
    """Рецепты в корзине покупок."""

    user = ForeignKey(
        MyUser,
        on_delete=CASCADE,
        verbose_name='Владелец',
        related_name='carts',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепты в списке покупок',
        related_name='in_carts',
    )
    date_added = DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True, editable=False
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'В корзине'
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'user',),
                name='\n%(app_label)s_%(class)s recipe is cart alredy\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} -> {self.recipe}'
