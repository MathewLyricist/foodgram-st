from http import HTTPStatus

import pytest
from django.db.models import Model
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.base_test import BaseTest
from tests.utils.general import (
    NOT_EXISTING_ID,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR
)
from tests.utils.models import shopping_cart_model
from tests.utils.recipe import RESPONSE_SCHEMA_SHORT_RECIPE
from tests.utils.shopping_cart import (
    ALLOWED_CONTENT_TYPES,
    URL_DOWNLOAD_SHOPPING_CART,
    URL_SHOPPING_CART
)

# Получаем модель корзины покупок из фабрики
ShoppingCart = shopping_cart_model()


@pytest.mark.django_db(transaction=True)
class TestShoppingCart(BaseTest):
    """Тесты для функционала корзины покупок."""

    def test_add_to_shopping_cart_unauthorized(
            self, api_client: APIClient, second_recipe: Model
    ):
        """Проверяет, что аноним не может добавить рецепт в корзину."""
        self.url_requires_authorization(
            client=api_client,
            url=URL_SHOPPING_CART.format(id=second_recipe.id)
        )

    @pytest.mark.usefixtures('all_shopping_cart')
    def test_add_again_to_shopping_cart(
            self, third_user_authorized_client: APIClient, third_recipe: Model
    ):
        """Проверяет невозможность повторного добавления рецепта в корзину."""
        self.url_bad_request_for_invalid_data(
            client=third_user_authorized_client,
            url=URL_SHOPPING_CART.format(id=third_recipe.id)
        )

    def test_add_non_existing_recipe_to_shopping_cart(
            self, third_user_authorized_client: APIClient
    ):
        """Проверяет обработку попытки добавить несуществующий рецепт."""
        self.url_is_missing_for_method(
            client=third_user_authorized_client,
            url=URL_SHOPPING_CART.format(id=NOT_EXISTING_ID),
            method='post'
        )

    def test_download_shopping_cart_unauthorized(
            self, api_client: APIClient
    ):
        """Проверяет, что аноним не может скачать список покупок."""
        self.url_requires_authorization(
            client=api_client,
            url=URL_DOWNLOAD_SHOPPING_CART
        )

    def test_add_to_shopping_cart_authorized(
            self, third_user_authorized_client: APIClient, third_user: Model,
            first_recipe: Model
    ):
        """Проверяет успешное добавление рецепта в корзину авторизованным пользователем."""
        self.url_creates_resource(
            client=third_user_authorized_client,
            url=URL_SHOPPING_CART.format(id=first_recipe.id),
            model=ShoppingCart,
            filters={'author': third_user, 'recipe': first_recipe},
            response_schema=RESPONSE_SCHEMA_SHORT_RECIPE
        )

    @pytest.mark.usefixtures('third_user', 'all_shopping_cart')
    def test_download_shopping_cart_authorized(
            self, third_user_authorized_client: APIClient
    ):
        """Проверяет успешное скачивание списка покупок."""
        response: Response = third_user_authorized_client.get(
            URL_DOWNLOAD_SHOPPING_CART
        )

        # Проверка доступности URL
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_DOWNLOAD_SHOPPING_CART)
        )

        # Проверка успешного статуса
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_DOWNLOAD_SHOPPING_CART)
        )

        # Проверка типа возвращаемого файла
        response_content_type = response.headers.get('Content-Type')
        assert response_content_type.split(';')[0] in ALLOWED_CONTENT_TYPES, (
            'Проверьте, что возвращаемый файл принадлежит к одному из '
            f'типов: {ALLOWED_CONTENT_TYPES}.'
        )

    def test_delete_shopping_cart_unauthorized(
            self, api_client: APIClient, all_shopping_cart: list
    ):
        """Проверяет, что аноним не может удалить рецепт из корзины."""
        id_cart: int = all_shopping_cart[0].recipe_id
        self.url_requires_authorization(
            client=api_client,
            url=URL_SHOPPING_CART.format(id=id_cart),
            method='delete'
        )

    def test_delete_not_added_from_shopping_cart(
            self, second_user_authorized_client: APIClient, all_shopping_cart: list
    ):
        """Проверяет удаление не добавленного в корзину рецепта."""
        id_recipe: int = all_shopping_cart[0].recipe_id
        self.url_bad_request_for_invalid_data(
            client=second_user_authorized_client,
            url=URL_SHOPPING_CART.format(id=id_recipe),
            method='delete'
        )

    def test_delete_non_existing_recipe_from_shopping_cart(
            self, third_user_authorized_client: APIClient
    ):
        """Проверяет обработку попытки удалить несуществующий рецепт."""
        self.url_is_missing_for_method(
            client=third_user_authorized_client,
            url=URL_SHOPPING_CART.format(id=NOT_EXISTING_ID),
            method='delete'
        )

    def test_delete_shopping_cart(
            self, third_user_authorized_client: APIClient, all_shopping_cart: list
    ):
        """Проверяет успешное удаление рецепта из корзины."""
        cart = all_shopping_cart[0]
        self.url_delete_resouce(
            client=third_user_authorized_client,
            url=URL_SHOPPING_CART.format(id=cart.recipe_id),
            model=ShoppingCart,
            item_id=cart.id
        )