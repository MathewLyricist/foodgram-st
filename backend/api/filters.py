from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """Фильтр для поиска ингредиентов по названию."""

    name = filters.CharFilter(
        lookup_expr='istartswith',
        help_text="Фильтр по началу названия ингредиента"
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов с расширенными возможностями."""

    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
        help_text="Фильтр по наличию в избранном (true/false)"
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        help_text="Фильтр по наличию в корзине покупок (true/false)"
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        help_text="Фильтр по ID автора рецепта"
    )

    class Meta:
        model = Recipe
        fields = ('author',)

    def _filter_by_user_relation(
            self,
            queryset: QuerySet,
            value: bool,
            relation_field: str
    ) -> QuerySet:
        """Общий метод для фильтрации по отношениям пользователя."""
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none() if value else queryset.all()

        filter_kwargs = {relation_field: user}
        return queryset.filter(**filter_kwargs).distinct() if value else queryset.exclude(**filter_kwargs)

    def filter_is_favorited(
            self,
            queryset: QuerySet,
            name: str,
            value: bool
    ) -> QuerySet:
        """Фильтрация рецептов по наличию в избранном."""
        return self._filter_by_user_relation(
            queryset,
            value,
            'recipe_favorite__author'
        )

    def filter_is_in_shopping_cart(
            self,
            queryset: QuerySet,
            name: str,
            value: bool
    ) -> QuerySet:
        """Фильтрация рецептов по наличию в корзине покупок."""
        return self._filter_by_user_relation(
            queryset,
            value,
            'shopping_cart__author'
        )