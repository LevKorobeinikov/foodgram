from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, ImageField, Model, Q,
                              UniqueConstraint)
from django.db.models.functions import Length

from foodgram.constants import (EMAIL_MAX_LENGTH, PASSWORD_MAX_LENGTH,
                                USERNAME_MAX_LENGTH, USERNAME_MIN_LENGTH,
                                USERS_HELP)

CharField.register_lookup(Length)


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
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Username contains restricted symbols.'
            ),
        ],
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
        max_length=PASSWORD_MAX_LENGTH,
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
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=USERNAME_MIN_LENGTH),
                name='\nusername is too short\n',
            ),
        )

    def __str__(self) -> str:
        return self.username


class Follow(Model):
    """Модель подписок."""
    author = ForeignKey(
        MyUser,
        related_name='following',
        verbose_name='Author',
        on_delete=CASCADE,
    )
    user = ForeignKey(
        MyUser,
        related_name='follower',
        verbose_name='Follower',
        on_delete=CASCADE,
    )

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = (
            UniqueConstraint(
                fields=('author', 'user'),
                name='unique_follow'
            ),
            CheckConstraint(
                check=~Q(author=F('user')),
                name='\nNo self sibscription\n'
            ),
        )

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.author.username}'
