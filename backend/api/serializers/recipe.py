from collections import OrderedDict
from typing import Optional

from django.db.models import Model
from rest_framework import serializers
from rest_framework.request import Request

from api.serializers.base_serializers import BaseRecipeSerializer
from api.serializers.recipe_ingredients import (
    RecipeIngredientsGetSerializer,
    RecipeIngredientsSetSerializer
)
from api.serializers.user import UserSerializer
from api.utils import many_unique_with_minimum_one_validate
from core.constants import MAX_INTEGER_VALUE, MIN_INTEGER_VALUE
from recipes.models import (
    Recipe,
    RecipeFavorite,
    RecipeIngredients,
    ShoppingCart
)


class RecipeSerializer(BaseRecipeSerializer):
    """Базовый сериализатор рецептов с расширенными полями.

    Добавляет:
    - Список ингредиентов через recipe_ingredients
    - Информацию об авторе
    - Текст рецепта
    """
    author = UserSerializer()
    ingredients = RecipeIngredientsGetSerializer(
        many=True,
        source='recipe_ingredients',
    )

    class Meta(BaseRecipeSerializer.Meta):
        abstract = True
        fields = (
            *BaseRecipeSerializer.Meta.fields,
            'ingredients',
            'author',
            'text'
        )


class RecipeGetSerializer(RecipeSerializer):
    """Сериализатор для получения данных о рецепте.

    Добавляет флаги:
    - is_favorited: в избранном ли рецепт
    - is_in_shopping_cart: в корзине ли рецепт
    """
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeSerializer.Meta):
        fields = (
            *RecipeSerializer.Meta.fields,
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = fields

    def get_is_exists(self, obj: Recipe, model: Model):
        request: Optional[Request] = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(
            author=request.user, recipe=obj
        ).exists()

    def get_is_favorited(self, obj: Recipe):
        """Проверяет наличие рецепта в избранном."""
        return self.get_is_exists(obj, RecipeFavorite)

    def get_is_in_shopping_cart(self, obj: Recipe):
        """Проверяет наличие рецепта в корзине покупок."""
        return self.get_is_exists(obj, ShoppingCart)


    class RecipeSerializer(BaseRecipeSerializer):
        """Сериализатор для создания или изменения рецептов."""
        author = UserSerializer()
        ingredients = RecipeIngredientsGetSerializer(
            many=True,
            source='recipe_ingredients',
        )

        class Meta(BaseRecipeSerializer.Meta):
            abstract = True
            fields = (
                *BaseRecipeSerializer.Meta.fields,
                'ingredients',
                'author',
                'text'
            )

class RecipeChangeSerializer(RecipeSerializer):
    author = UserSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientsSetSerializer(
        many=True,
        source='recipe_ingredients',
    )
    cooking_time = serializers.IntegerField(
        max_value=MAX_INTEGER_VALUE,
        min_value=MIN_INTEGER_VALUE
    )

    class Meta(RecipeSerializer.Meta):
        read_only_fields = ('author',)

    def validate(self, data: OrderedDict):
        """Валидация ингредиентов перед сохранением."""
        ingredients = data.get('recipe_ingredients')
        many_unique_with_minimum_one_validate(
            data_list=ingredients,
            field_name='ingredients',
            singular='ингредиент',
            plural='ингредиенты'
        )
        return data

    def create(self, validated_data: dict):
        ingredients = validated_data.pop('recipe_ingredients')
        recipe = Recipe.objects.create(**validated_data)

        ingredient_recipe = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(ingredient_recipe)
        return recipe

    def update(self, instance: Recipe, validated_data: dict):
        ingredients = validated_data.pop('recipe_ingredients')
        super().update(instance, validated_data)

        instance.recipe_ingredients.all().delete()
        ingredient_recipe = [
            RecipeIngredients(
                recipe=instance,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(ingredient_recipe)
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance, context=self.context
        ).data