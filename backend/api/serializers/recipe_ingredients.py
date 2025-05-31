from rest_framework import serializers

from core.constants import MAX_INTEGER_VALUE, MIN_INTEGER_VALUE
from recipes.models import Ingredient, RecipeIngredients


class RecipeIngredientsSetSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления связи рецепт-ингредиент"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        max_value=MAX_INTEGER_VALUE,
        min_value=MIN_INTEGER_VALUE
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeIngredientsGetSerializer(serializers.ModelSerializer):
    """Сериалайзатор для чтения информации о связи рецепт-ингредиент"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')
