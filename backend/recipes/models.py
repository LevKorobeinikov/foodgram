from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import (CASCADE, CharField, CheckConstraint,
                              DateTimeField, EmailField, F, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, Q, SlugField,
                              TextField, UniqueConstraint)
from django.db.models.functions import Length

from recipes.constants import (COOKING_TIME_MIN, EMAIL_MAX_LENGTH,
                               INGREDIENT_AMOUNT_MIN,
                               INGREDIENT_NAME_MAX_LENGTH,
                               MEASUREMENT_UNIT_MAX_LENGTH,
                               RECIPE_NAME_MAX_LENGTH, TAG_NAME_MAX_LENGTH,
                               TAG_SLUG_MAX_LENGTH, USERNAME_MAX_LENGTH,
                               USERS_HELP)

CharField.register_lookup(Length)


class ProjectUser(AbstractUser):
    """Модель пользователя."""

    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        help_text=USERS_HELP,
    )
    username = CharField(
        verbose_name='Юзернейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=USERS_HELP,
        validators=[RegexValidator(regex=r'^[\w.@+-]+$')],
    )
    first_name = CharField(
        verbose_name='Имя',
        max_length=USERNAME_MAX_LENGTH,
        help_text=USERS_HELP,
    )
    last_name = CharField(
        verbose_name='Фамилия',
        max_length=USERNAME_MAX_LENGTH,
        help_text=USERS_HELP,
    )
    avatar = ImageField(
        blank=True,
        null=True,
        upload_to='media/avatars/',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password',
    )

    class Meta:
        verbose_name = 'Пользователя'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(Model):
    """Модель подписок."""
    author = ForeignKey(
        ProjectUser,
        related_name='authors',
        verbose_name='Автор',
        on_delete=CASCADE,
    )
    user = ForeignKey(
        ProjectUser,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('author', 'user'),
                name='unique_follow'
            ),
            CheckConstraint(
                check=~Q(author=F('user')),
                name='No self sibscription'
            ),
        )

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'


class Ingredient(Model):
    name = CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название',
        help_text='Введите название ингредиента',
    )
    measurement_unit = CharField(
        max_length=MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единица измерения',
        help_text='Укажите единицу измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
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
        verbose_name='Название',
        help_text='Введите название тега',
    )
    slug = SlugField(
        max_length=TAG_SLUG_MAX_LENGTH,
        unique=True,
        verbose_name='Слаг',
        help_text='Введите уникальный слаг для тега',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(Model):
    name = CharField(
        max_length=RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название',
        help_text='Введите название рецепта',
    )
    text = TextField(
        verbose_name='Описание рецепта',
        help_text='Добавьте описание рецепта',
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
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
        ProjectUser,
        on_delete=CASCADE,
        verbose_name='Автор рецепта',
    )
    tags = ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Теги рецепта',
        help_text='Добавьте теги для рецепта.',
    )
    pub_date = DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='дата публикации рецепта',
    )

    class Meta:
        ordering = ('name',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(Model):
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='ingredients',
        verbose_name='Продукт'
    )
    amount = PositiveSmallIntegerField(
        validators=(MinValueValidator(
            INGREDIENT_AMOUNT_MIN,
            f'Минимальное количество: {INGREDIENT_AMOUNT_MIN}',
        ),),
        verbose_name='Количество',
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Мера'
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


class BaseUserRecipeRelation(Model):

    user = ForeignKey(
        ProjectUser,
        on_delete=CASCADE,
        verbose_name='Пользователь',
    )
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        ordering = ('-id',)

    def __str__(self):
        return f'Рецепт "{self.recipe}" у пользователя {self.user}'


class Favorite(BaseUserRecipeRelation):

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe',
            ),
        )


class ShoppingList(BaseUserRecipeRelation):

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_list'
        constraints = (
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_list_recipe',
            ),
        )
