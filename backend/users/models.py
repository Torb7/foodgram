from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from recipes.models import Recipe
from recipes.constants import (
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
)


class User(AbstractUser):
    """Модель пользователя"""

    username = models.CharField(
        'Юзернейм',
        unique=True,
        max_length=MAX_LENGTH_USERNAME,
        validators=[UnicodeUsernameValidator()],
    )

    email = models.EmailField(
        'Почта', unique=True, max_length=MAX_LENGTH_EMAIL
    )

    first_name = models.CharField('Имя', max_length=MAX_LENGTH_FIRST_NAME)

    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH_LAST_NAME)

    avatar = models.ImageField(
        upload_to='avatar/images/', null=True, default=None
    )

    favorite_recipes = models.ManyToManyField(
        'recipes.Recipe',
        through='Favorites',
        blank=True,
        related_name='in_favorites',
        verbose_name='Избранное',
    )

    shopping_cart = models.ManyToManyField(
        'recipes.Recipe',
        through='ShoppingCart',
        blank=True,
        related_name='in_shopping_cart',
        verbose_name='Список покупок',
    )

    following = models.ManyToManyField(
        'self',
        through='Follow',
        through_fields=('user', 'following'),
        symmetrical=False,
        blank=True,
        related_name='followers',
        verbose_name='Подписки',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following_relations'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers_relations',
        verbose_name='Подписки',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'), name='unique_follow'
            ),
            models.CheckConstraint(
                condition=~models.Q(user__exact=models.F('following')),
                name='follow_not_self',
            ),
        ]

    def __str__(self):
        return 'Подписан на'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_user',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True


class Favorites(UserRecipeRelation):
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_favorites'
            )
        ]

    def __str__(self):
        return f'Рецепт в избранном у {self.user.email}'


class ShoppingCart(UserRecipeRelation):
    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'

        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'Рецепт в корзине покупок у {self.user.email}'
