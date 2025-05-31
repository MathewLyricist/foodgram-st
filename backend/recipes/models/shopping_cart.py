from django.contrib.auth import get_user_model
from django.db import models

from recipes.models.abstract_models import BaseActionRecipeModel

User = get_user_model()


class ShoppingCart(BaseActionRecipeModel):
    """
    Модель для хранения рецептов в корзине покупок пользователя.

    Наследует базовую функциональность из BaseActionRecipeModel:
    - author (ForeignKey): пользователь, добавивший рецепт
    - recipe (ForeignKey): рецепт в корзине
    - created_at (DateTime): дата добавления
    """

    class Meta(BaseActionRecipeModel.Meta):
        """Мета-класс с настройками модели."""

        # Ограничение уникальности: один рецепт на пользователя
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

        # Настройки именования
        default_related_name = 'shopping_cart'
        verbose_name = 'рецепт к покупке'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self) -> str:
        """Строковое представление объекта для админки и отладки."""
        return f'Рецепт #{self.recipe.id}'