from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE, BooleanField,
    CharField, CheckConstraint,
    DateTimeField, EmailField,
    F, ForeignKey,
    Model, Q,
    UniqueConstraint,
)
from django.db.models.functions import Length
from django.utils.translation import gettext_lazy as _

from foodgram.constants import (
    USERNAME_MAX_LENGTH, USERNAME_MIN_LENGTH,
    EMAIL_MAX_LENGTH, USERS_HELP,
)

CharField.register_lookup(Length)

User = get_user_model()


class MyUser(AbstractUser):
    """Модель пользователя."""

    email = EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        help_text=USERS_HELP,
    )
    username = CharField(
        verbose_name='Уникальный юзернейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=USERS_HELP,
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
    password = CharField(
        verbose_name=_('Пароль'),
        max_length=128,
        help_text=USERS_HELP,
    )
    is_active = BooleanField(
        verbose_name='Активирован',
        default=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=USERNAME_MIN_LENGTH),
                name='\nusername is too short\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Follow(Model):
    """Модель подписок."""
    author = ForeignKey(
        verbose_name='Автор рецепта',
        related_name='subscribers',
        to=MyUser,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Подписчики',
        related_name='subscriptions',
        to=MyUser,
        on_delete=CASCADE,
    )
    date_added = DateTimeField(
        verbose_name='Дата создания подписки',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            UniqueConstraint(
                fields=('author', 'user'),
                name='\nRepeat subscription\n',
            ),
            CheckConstraint(
                check=~Q(author=F('user')),
                name='\nNo self sibscription\n'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
