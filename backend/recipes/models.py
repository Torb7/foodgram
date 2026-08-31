from django.db import models


from .constants import (
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
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
