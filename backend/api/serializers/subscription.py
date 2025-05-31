from django.conf import settings
from django.db.models.query import QuerySet
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.validators import UniqueTogetherValidator

from api.serializers.base_serializers import BaseRecipeSerializer
from api.serializers.user import UserSerializer
from api.validators import SubscribeUniqueValidator
from users.models import Subscription, User


class SubscriptionGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о подписках."""

    is_subscribed = serializers.SerializerMethodField(method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.IntegerField(source='recipes.count')

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj: User):
        """Проверяет, подписан ли текущий пользователь на автора."""
        request: Request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.authors.filter(user=request.user).exists()

    def get_recipes(self, obj: User):
        """Возвращает список рецептов автора с учетом лимита."""
        request: Request = self.context.get('request')
        recipes_limit: int = (
            request.GET.get('recipes_limit') if request
            else settings.RECIPES_LIMIT_MAX
        )
        queryset: QuerySet = obj.recipes.all()

        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = BaseRecipeSerializer
        return serializer(queryset, many=True).data

        return SerializerBaseRecipe(queryset, many=True).data

class SubscriptionChangedSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/удаления подписок."""

    author_recipe = UserSerializer
    user = UserSerializer

    class Meta:
        model = Subscription
        fields = ('author_recipe', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('author_recipe', 'user'),
                message='Нельзя повторно подписаться на пользователя'
            ),
            SubscribeUniqueValidator(
                fields=('author_recipe', 'user')
            )
        ]

    def to_representation(self, instance):
        return SubscriptionGetSerializer(
            instance.author_recipe,
            context={'request': self.context.get('request')}
        ).data