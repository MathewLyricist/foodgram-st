import pytest
from django.db.models import Model
from pytest_lazyfixture import lazy_fixture
from rest_framework.response import Response
from rest_framework.test import APIClient

from recipes.models.recipe import Recipe
from tests.base_test import BaseTest
from tests.utils.general import NOT_EXISTING_ID
from tests.utils.models import subscription_model
from tests.utils.subscription import (
    RESPONSE_SCHEMA_SUBSCRIPTION,
    RESPONSE_SCHEMA_SUBSCRIPTIONS,
    URL_CREATE_SUBSCRIBE,
    URL_GET_SUBSCRIPTIONS
)

# Получаем модель подписки из фабрики
Subscription = subscription_model()


@pytest.mark.django_db(transaction=True)
class TestSubscription(BaseTest):
    """Тесты для функционала подписок на авторов."""

    def test_add_subscribe_unauthorized(
            self, api_client: APIClient, second_user: Model
    ):
        """Проверяет, что аноним не может подписаться на автора."""
        self.url_requires_authorization(
            client=api_client,
            url=URL_CREATE_SUBSCRIBE.format(id=second_user.id)
        )

    @pytest.mark.usefixtures('third_user_subscribed_to_second')
    def test_add_duplicated_subscription(
            self, third_user_authorized_client: APIClient, second_user: Model
    ):
        """Проверяет невозможность повторной подписки на автора."""
        self.check_db_no_changes_made(
            client=third_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=second_user.id),
            model=Subscription
        )

    def test_add_self_subscription(
            self, third_user_authorized_client: APIClient, third_user: Model
    ):
        """Проверяет невозможность подписки на самого себя."""
        self.check_db_no_changes_made(
            client=third_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=third_user.id),
            model=Subscription
        )

    def test_add_subscription_to_non_existing_author(
            self, third_user_authorized_client: APIClient
    ):
        """Проверяет обработку попытки подписаться на несуществующего автора."""
        self.url_is_missing_for_method(
            client=third_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=NOT_EXISTING_ID),
            method='post'
        )

    @pytest.mark.usefixtures('all_recipes')
    def test_add_subscribe_authorized(
            self, third_user_authorized_client: APIClient, first_user: Model,
            third_user: Model
    ):
        """Проверяет успешную подписку на автора."""
        self.url_creates_resource(
            client=third_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=first_user.id),
            model=Subscription,
            filters={'author_recipe': first_user, 'user': third_user},
            response_schema=RESPONSE_SCHEMA_SUBSCRIPTION
        )

    @pytest.mark.parametrize('recipes_limit', [1, 5, 10])
    @pytest.mark.usefixtures('all_recipes')
    def test_add_subscribe_authorized_with_recipes_limit_param(
            self, third_user_authorized_client: APIClient, second_user: Model,
            third_user: Model, recipes_limit: int
    ):
        """Проверяет подписку с параметром ограничения количества рецептов."""
        url = URL_CREATE_SUBSCRIBE.format(id=second_user.id) + (
                '?recipes_limit=' + str(recipes_limit)
        )
        response: Response = self.url_creates_resource(
            client=third_user_authorized_client,
            url=url,
            model=Subscription,
            filters={'author_recipe': second_user, 'user': third_user},
            response_schema=RESPONSE_SCHEMA_SUBSCRIPTION
        )

        # Проверка ограничения количества рецептов в ответе
        response_json: dict = response.json()
        self.url_limits_results_count(
            data=response_json['recipes'],
            model=Recipe,
            filters={'author': second_user},
            limit=recipes_limit
        )

    @pytest.mark.parametrize(
        'author',
        [lazy_fixture('first_user'), lazy_fixture('second_user')]
    )
    @pytest.mark.usefixtures('third_user_subscriptions', 'author')
    def test_get_subscription_list(
            self, third_user_authorized_client: APIClient, third_user: Model
    ):
        """Проверяет получение списка подписок."""
        response: Response = third_user_authorized_client.get(
            URL_GET_SUBSCRIPTIONS
        )
        self.url_get_resource(
            response=response,
            url=URL_GET_SUBSCRIPTIONS,
            response_schema=RESPONSE_SCHEMA_SUBSCRIPTIONS
        )

        # Проверка соответствия количества подписок в ответе и БД
        response_json: dict = response.json()
        self.url_reponse_count_matches_db_count(
            data=response_json.get('results', []),
            model=Subscription,
            filters={'user': third_user}
        )

    @pytest.mark.parametrize('limit', [1, 5])
    @pytest.mark.usefixtures('third_user_subscriptions')
    def test_get_subscription_list_with_limit_param(
            self, third_user_authorized_client: APIClient, limit: int
    ):
        """Проверяет пагинацию списка подписок."""
        url = URL_GET_SUBSCRIPTIONS + '?limit=' + str(limit)
        response: Response = third_user_authorized_client.get(url)
        self.url_get_resource(
            response=response,
            url=url,
            response_schema=RESPONSE_SCHEMA_SUBSCRIPTIONS
        )
        self.url_pagination_results(data=response.json(), limit=limit)

    @pytest.mark.parametrize('recipes_limit', [1, 5, 10])
    @pytest.mark.usefixtures('third_user_subscribed_to_second', 'all_recipes')
    def test_get_subscription_list_with_recipes_limit_param(
            self, third_user_authorized_client: APIClient, second_user: Model,
            recipes_limit: int
    ):
        """Проверяет ограничение количества рецептов в списке подписок."""
        url = URL_GET_SUBSCRIPTIONS + '?recipes_limit=' + str(recipes_limit)
        response: Response = third_user_authorized_client.get(url)
        self.url_get_resource(
            response=response,
            url=URL_GET_SUBSCRIPTIONS,
            response_schema=RESPONSE_SCHEMA_SUBSCRIPTIONS
        )

        # Проверка ограничения количества рецептов у автора
        response_json: dict = response.json()
        self.url_limits_results_count(
            data=response_json['results'][0]['recipes'],
            model=Recipe,
            filters={'author': second_user},
            limit=recipes_limit
        )

    def test_delete_subscription_unauthorized(
            self, api_client: APIClient, first_user: Model
    ):
        """Проверяет, что аноним не может отписаться."""
        id_subscription: int = first_user.id
        self.url_requires_authorization(
            client=api_client,
            url=URL_CREATE_SUBSCRIBE.format(id=id_subscription),
            method='delete'
        )

    @pytest.mark.usefixtures('third_user_subscribed_to_first')
    def test_delete_not_added_from_subscription(
            self, second_user_authorized_client: APIClient, first_user: Model,
    ):
        """Проверяет, что нельзя отписаться от чужой подписки."""
        id_subscription: int = first_user.id
        self.url_bad_request_for_invalid_data(
            client=second_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=id_subscription),
            method='delete'
        )

    def test_delete_non_existing_recipe_from_subscription(
            self, third_user_authorized_client: APIClient
    ):
        """Проверяет обработку попытки отписаться от несуществующего автора."""
        self.url_is_missing_for_method(
            client=third_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=NOT_EXISTING_ID),
            method='delete'
        )

    @pytest.mark.usefixtures('third_user_subscribed_to_first')
    def test_delete_subscription(
            self, third_user_authorized_client: APIClient, first_user: Model
    ):
        """Проверяет успешную отписку от автора."""
        id_subscription: int = first_user.id
        self.url_delete_resouce(
            client=third_user_authorized_client,
            url=URL_CREATE_SUBSCRIBE.format(id=id_subscription),
            model=Subscription,
            item_id=id_subscription
        )