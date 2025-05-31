from django.db import models

from core.constants import LENGTH_CHARFIELD_64, LENGTH_CHARFIELD_128
from recipes.models.base_models import CookbookBaseModel


class Ingredient(CookbookBaseModel):
    """Модель ингредиентов."""

    name = models.CharField(
        verbose_name='Наименование ингредиента',
        max_length=LENGTH_CHARFIELD_128,
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерений',
        max_length=LENGTH_CHARFIELD_64
    )

    class Meta(CookbookBaseModel.Meta):
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name.capitalize()} - {self.measurement_unit}.'