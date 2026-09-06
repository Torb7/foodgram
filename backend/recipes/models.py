from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


from .constants import (
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_INGREDIENT_MEASUREMENT,
    MAX_LENGTH_RECIPE_NAME,
)


class Tag(models.Model):
    """Модель тега"""

    name = models.CharField('Имя', unique=True, max_length=MAX_LENGTH_TAG_NAME)

    slug = models.SlugField(
        'Слаг', unique=True, max_length=MAX_LENGTH_TAG_SLUG
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('slug',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиента"""

    name = models.CharField('Название', max_length=MAX_LENGTH_INGREDIENT_NAME)

    measurement_unit = models.CharField(
        'Измерение', max_length=MAX_LENGTH_INGREDIENT_MEASUREMENT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""

    name = models.CharField('Название', max_length=MAX_LENGTH_RECIPE_NAME)

    text = models.TextField('Описание')

    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', validators=(MinValueValidator(1),)
    )

    image = models.ImageField(upload_to='recipes/images/')

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата и время публикации'
    )

    short_code = models.CharField(
        max_length=5, unique=True, null=True, editable=False
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients', verbose_name='Ингредиенты'
    )

    tags = models.ManyToManyField(Tag, verbose_name='Теги')

    class Meta:
        ordering = ('-created_at',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Модель ингредиентов рецепта"""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes'
    )

    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента', validators=(MinValueValidator(1),)
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
