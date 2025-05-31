from django.contrib.auth import get_user_model
from django.db import models

from recipes.models.base_models import CookbookBaseModel
from recipes.models.fields import UserForeignKey
from recipes.models.recipe import Recipe

User = get_user_model()


class BaseActionRecipeModel(CookbookBaseModel):
    """Заготовка для моделей, связанных с добавлением рецептов."""

    author = UserForeignKey(verbose_name='Владелец корзины покупок')
    recipe = models.ForeignKey(
        to=Recipe, verbose_name='Рецепт', on_delete=models.CASCADE
    )

    class Meta(CookbookBaseModel.Meta):
        abstract = True