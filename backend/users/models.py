from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, ImageField, Model, Q,
                              UniqueConstraint)
from django.db.models.functions import Length

from recipes.constants import EMAIL_MAX_LENGTH, USERNAME_MAX_LENGTH, USERS_HELP

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

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self) -> str:
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
        verbose_name = 'Подписки'
        verbose_name_plural = 'Subscriptions'
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

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
