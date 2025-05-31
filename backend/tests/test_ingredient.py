import pytest
from pytest_lazyfixture import lazy_fixture
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.base_test import BaseTest
from tests.utils.general import NOT_EXISTING_ID
from tests.utils.ingredient import (
    DENY_CHANGE_METHOD,
    INGREDIENT_SEARCH_DATA,
    RESPONSE_SCHEMA_INGREDIENT,
    RESPONSE_SCHEMA_INGREDIENTS,
    URL_GET_INGREDIENT,
    URL_INGREDIENTS
)
from tests.utils.models import ingredient_model

# Получаем модель ингредиента из фабрики
Ingredient = ingredient_model()


@pytest.mark.django_db(transaction=True)
class TestIngredient(BaseTest):
    """Тесты для работы с ингредиентами."""

    @pytest.mark.parametrize(
        'method, method_info', DENY_CHANGE_METHOD.items()
    )
    @pytest.mark.usefixtures('ingredients')
    def test_bad_request_methods(
            self, first_user_authorized_client: APIClient, method: str,
            method_info: dict
    ):
        """Проверяет запрещенные методы для работы с ингредиентами."""
        self.url_is_not_allowed_for_method(
            client=first_user_authorized_client,
            url=method_info['url'],
            method=method
        )

    @pytest.mark.parametrize(
        'client',
        [
            lazy_fixture('api_client'),  # Неавторизованный клиент
            lazy_fixture('first_user_authorized_client')  # Авторизованный клиент
        ]
    )
    @pytest.mark.usefixtures('ingredients')
    def test_get_ingredients(
            self, client: APIClient
    ):
        """Проверяет получение списка ингредиентов (доступно всем)."""
        self.url_get_resource(
            client=client,
            url=URL_INGREDIENTS,
            response_schema=RESPONSE_SCHEMA_INGREDIENTS
        )

    @pytest.mark.parametrize('name', INGREDIENT_SEARCH_DATA)
    @pytest.mark.usefixtures('ingredients')
    def test_get_ingredients_with_name_filter(
            self, first_user_authorized_client: APIClient, name: str
    ):
        """Проверяет фильтрацию ингредиентов по имени."""
        url = URL_INGREDIENTS + '?name=' + name
        response: Response = first_user_authorized_client.get(url)

        # Проверяем корректность ответа
        self.url_get_resource(
            response=response,
            url=url,
            response_schema=RESPONSE_SCHEMA_INGREDIENTS
        )

        # Проверяем работу фильтрации
        self.url_filters_by_query_parameters(
            response=response,
            model=Ingredient,
            filters={'name__startswith': name}
        )

    @pytest.mark.parametrize(
        'client',
        [
            lazy_fixture('api_client'),
            lazy_fixture('first_user_authorized_client')
        ]
    )
    def test_get_ingredient_detail(self, client: APIClient, ingredients: list):
        """Проверяет получение детальной информации об ингредиенте (доступно всем)."""
        self.url_get_resource(
            client=client,
            url=URL_GET_INGREDIENT.format(id=ingredients[0].id),
            response_schema=RESPONSE_SCHEMA_INGREDIENT
        )

    @pytest.mark.usefixtures('ingredients')
    def test_non_existing_ingredient(
            self, first_user_authorized_client: APIClient
    ):
        """Проверяет обработку запроса несуществующего ингредиента."""
        self.url_is_missing_for_method(
            client=first_user_authorized_client,
            url=URL_GET_INGREDIENT.format(id=NOT_EXISTING_ID),
            method='get'
        )