import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.serializers.user import UserSerializer
from recipes.models.abstract_models import BaseActionRecipeModel
from recipes.models.recipe import Recipe


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для обработки изображений в формате Base64.

    Преобразует строку Base64 в файл изображения при валидации.
    """

    def to_internal_value(self, data: str):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class AvatarSerializer(serializers.Serializer):
    """Сериалайзатор для аватарки."""

    avatar = Base64ImageField(required=False)


class BaseRecipeSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для рецептов.


    Содержит основные поля, используемые в кратких представлениях рецептов.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    """Абстрактный сериализатор для действий с рецептами.

    Используется для добавления рецептов в избранное, корзину и т.д.
    """

    author = UserSerializer
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )

    class Meta:
        model = None  # Назначаем у дочерних классов
        fields = ('author', 'recipe')
        error_message = 'Этот рецепт уже добавлен.'

    @classmethod
    def get_validators(cls):
        """Генерирует валидаторы для проверки уникальности связки автор-рецепт."""
        return [
            UniqueTogetherValidator(
                queryset=cls.Meta.model.objects.all(),
                fields=('author', 'recipe'),
                message=cls.Meta.error_message
            )
        ]

    def __init__(self, *args, **kwargs):
        """Инициализация с добавлением валидаторов."""
        super().__init__(*args, **kwargs)
        self.Meta.validators = self.get_validators()

    def to_representation(self, instance: BaseActionRecipeModel):
        """Преобразует экземпляр в сериализованное представление."""
        return BaseRecipeSerializer(instance.recipe).data
