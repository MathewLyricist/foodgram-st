from api.serializers.base_serializers import BaseRecipeActionSerializer
from core.constants import REPEAT_ADDED_FAVORITE_ERROR
from recipes.models import RecipeFavorite


class RecipeFavoriteSerializer(BaseRecipeActionSerializer):
    """Сериалайзатор для избранных рецептов."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = RecipeFavorite
        error_message = REPEAT_ADDED_FAVORITE_ERROR
