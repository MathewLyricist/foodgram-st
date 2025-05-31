from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from core.constants import (
    FRONTEND_DETAIL_URL,
    LENGTH_CHARFIELD_256,
    MAX_COOKING_TIME_ERROR,
    MAX_INTEGER_VALUE,
    MAX_LENGTH_SHORT_LINK,
    MIN_COOKING_TIME_ERROR,
    MIN_INTEGER_VALUE,
    RECIPE_IMAGE_PATH
)
from core.utils import generate_short_link
from recipes.models.base_models import CookbookBaseModel
from recipes.models.fields import UserForeignKey
from recipes.models.ingredient import Ingredient

User = get_user_model()


class Recipe(CookbookBaseModel):
    """Модель рецептов."""

    author = UserForeignKey(verbose_name='Автор рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredients', verbose_name='Ингредиенты'
    )
    name = models.CharField(
        verbose_name='Наименование рецепта',
        max_length=LENGTH_CHARFIELD_256
    )
    image = models.ImageField(
        verbose_name='Путь до картинки', blank=True,
        upload_to=RECIPE_IMAGE_PATH
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_INTEGER_VALUE,
                message=MIN_COOKING_TIME_ERROR
            ),
            MaxValueValidator(
                MAX_INTEGER_VALUE,
                message=MAX_COOKING_TIME_ERROR
            )
        ]
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка', default=generate_short_link,
        max_length=MAX_LENGTH_SHORT_LINK
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        default=now, editable=False
    )

    class Meta(CookbookBaseModel.Meta):
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self) -> str:
        return f'[{self.id}] {self.name}'

    def get_frontend_absolute_url(self) -> str:
        return FRONTEND_DETAIL_URL.format(pk=self.pk)