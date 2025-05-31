from django.contrib.auth import get_user_model
from django.db import models

from recipes.models.abstract_models import BaseActionRecipeModel

User = get_user_model()


class RecipeFavorite(BaseActionRecipeModel):
    """Модель избранных рецептов."""

    class Meta(BaseActionRecipeModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_recipe_favorite'
            )
        ]
        default_related_name = 'recipe_favorite'
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self) -> str:
        return f'Рецепт #{self.recipe.id}'