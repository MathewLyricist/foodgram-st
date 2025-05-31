import re
from functools import wraps
from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.db.models import Model
from pytest_lazyfixture import lazy_fixture
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.base_test import BaseTest
from tests.utils.general import (
    NOT_EXISTING_ID,
    RESPONSE_EXPECTED_STRUCTURE,
    URL_OK_ERROR
)
from tests.utils.user import (
    AVATAR,
    FIRST_VALID_USER,
    NEW_PASSWORD,
    RESPONSE_SCHEMA_AVATAR,
    RESPONSE_SCHEMA_USER,
    RESPONSE_SCHEMA_USERS,
    URL_AVATAR,
    URL_CREATE_USER,
    URL_GET_USER,
    URL_LOGIN,
    URL_ME,
    URL_SET_PASSWORD
)

# Получаем модель пользователя Django
User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestUsers(BaseTest):
    """Тесты для работы с пользователями и их профилями."""

    # Методы, запрещенные для неавторизованных пользователей
    UNAUTHORIZED_BANNED_METHODS = {
        'post_me': {'url': URL_ME, 'method': 'post'},
        'put_avatar': {'url': URL_AVATAR, 'method': 'put'},
        'delete_avatar': {'url': URL_AVATAR, 'method': 'delete'},
        'post_set_password': {'url': URL_SET_PASSWORD, 'method': 'post'},
    }

    @pytest.mark.parametrize(
        'method_name, data', UNAUTHORIZED_BANNED_METHODS.items()
    )
    @pytest.mark.usefixtures('method_name')
    def test_bad_request_unauthorized(self, api_client: APIClient, data: dict):
        """Проверяет, что неавторизованные запросы к защищенным методам запрещены."""
        self.url_requires_authorization(
            client=api_client,
            url=data['url'],
            method=data['method']
        )

    @pytest.mark.usefixtures('all_user')
    def test_non_existing_profile(self, api_client: APIClient):
        """Проверяет обработку запроса к несуществующему профилю."""
        self.url_is_missing_for_method(
            client=api_client,
            url=URL_GET_USER.format(id=NOT_EXISTING_ID),
            method='get'
        )

    @pytest.mark.usefixtures('first_user')
    def test_reset_password_wrong_data(
            self, first_user_authorized_client: APIClient
    ):
        """Проверяет смену пароля с неверным текущим паролем."""
        self.url_bad_request_for_invalid_data(
            client=first_user_authorized_client,
            url=URL_SET_PASSWORD,
            data={
                'current_password': 'wrongPassword',
                'new_password': NEW_PASSWORD
            }
        )

    @pytest.mark.parametrize(
        'client',
        [
            lazy_fixture('api_client'),  # Неавторизованный пользователь
            lazy_fixture('first_user_authorized_client')  # Авторизованный пользователь
        ]
    )
    @pytest.mark.usefixtures('all_user')
    def test_get_users(self, client: APIClient):
        """Проверяет получение списка пользователей (доступно всем)."""
        self.url_get_resource(
            client=client,
            url=URL_CREATE_USER,
            response_schema=RESPONSE_SCHEMA_USERS
        )

    @pytest.mark.parametrize(
        'client',
        [
            lazy_fixture('api_client'),
            lazy_fixture('third_user_authorized_client')
        ]
    )
    @pytest.mark.usefixtures('third_user_subscribed_to_first')
    def test_get_user_detail(self, client: APIClient, first_user: Model):
        """Проверяет получение детальной информации о пользователе (доступно всем)."""
        self.url_get_resource(
            client=client,
            url=URL_GET_USER.format(id=first_user.id),
            response_schema=RESPONSE_SCHEMA_USER
        )

    @pytest.mark.parametrize('limit', [1, 999999])
    @pytest.mark.usefixtures('all_user')
    def test_get_users_paginated(
            self, first_user_authorized_client: APIClient, limit: int
    ):
        """Проверяет пагинацию списка пользователей."""
        url = URL_CREATE_USER + '?limit=' + str(limit)
        response: Response = first_user_authorized_client.get(url)
        self.url_get_resource(
            response=response,
            url=url,
            response_schema=RESPONSE_SCHEMA_USERS
        )
        self.url_pagination_results(data=response.json(), limit=limit)

    def test_get_users_me(
            self, first_user_authorized_client: APIClient, first_user: Model
    ):
        """Проверяет получение данных текущего пользователя."""
        response: Response = first_user_authorized_client.get(URL_ME)
        self.url_get_resource(
            response=response,
            url=URL_ME,
            response_schema=RESPONSE_SCHEMA_USER
        )

        # Проверка поля avatar в ответе
        response_json: dict = response.json()
        avatar: str = response_json.get('avatar')
        avatar_db: str = User.objects.get(id=first_user.id).avatar.name

        if avatar_db:
            assert avatar is not None, (
                'Убедитесь, что в ответе поле `avatar` не пустое.'
            )
            pattern_avatar = (
                r'^https?://[a-zA-Z0-9.-]+/media/users/[\w-]+\.(jpeg|png)$'
            )
            assert bool(re.match(pattern_avatar, avatar)), (
                RESPONSE_EXPECTED_STRUCTURE
            )
        else:
            assert avatar is None, (
                'Убедитесь, что после корректного запроса на удаление аватара '
                'в ответе на запрос к данным пользователя в поле `avatar` '
                'вернётся `null` или пустая строка.'
            )

    def check_avatar_update(action_func):
        """Декоратор для проверки обновления аватара в БД."""

        @wraps(action_func)
        def wrapper(
                self, client: APIClient, user: Model, *args, **kwargs
        ):
            old_item = User.objects.get(id=user.id).avatar
            action_func(self, client, user, *args, **kwargs)
            new_item = User.objects.get(id=user.id).avatar
            assert old_item != new_item, (
                'Поле `avatar` в БД должно обновиться.'
            )

        return wrapper

    @check_avatar_update
    @pytest.mark.parametrize(
        'client, user',
        [(
                lazy_fixture('first_user_authorized_client'),
                lazy_fixture('first_user')
        )]
    )
    def test_put_users_me_avatar(
            self, client: APIClient, user: Model
    ):
        """Проверяет обновление аватара пользователя."""
        response: Response = client.put(
            URL_AVATAR, {'avatar': AVATAR}
        )
        self.url_get_resource(
            response=response,
            url=URL_AVATAR,
            response_schema=RESPONSE_SCHEMA_AVATAR
        )
        # Дополнительная проверка отображения в профиле
        self.test_get_users_me(client, user)

    @pytest.mark.parametrize(
        'client, user',
        [(
                lazy_fixture('first_user_authorized_client'),
                lazy_fixture('first_user')
        )]
    )
    def test_delete_me_avatar_authorized(
            self, client: APIClient, user: Model
    ):
        """Проверяет удаление аватара пользователя."""
        # Сначала добавляем аватар
        self.test_put_users_me_avatar(client, user)

        old_item = User.objects.get(id=user.id).avatar
        response: Response = client.delete(URL_AVATAR)
        self.url_returns_no_content(
            response=response,
            url=URL_AVATAR
        )
        # Проверка отображения в профиле
        self.test_get_users_me(client, user)
        new_item = User.objects.get(id=user.id).avatar
        assert old_item != new_item, (
            'Поле `avatar` в БД должно обновиться.'
        )

    def test_reset_password(
            self, first_user_authorized_client: APIClient, first_user: Model
    ):
        """Проверяет смену пароля и последующий вход с новым паролем."""
        old_password = User.objects.get(id=first_user.id).password
        response: Response = first_user_authorized_client.post(
            URL_SET_PASSWORD, {
                'current_password': FIRST_VALID_USER['password'],
                'new_password': NEW_PASSWORD
            }
        )
        self.url_returns_no_content(
            response=response,
            url=URL_SET_PASSWORD
        )
        assert (old_password != User.objects.get(id=first_user.id).password), (
            'Убедитесь, что при корректном текущем пароле данные в БД '
            'будут изменены.'
        )

        # Проверка входа с новым паролем
        response: Response = first_user_authorized_client.post(URL_LOGIN, {
            'password': NEW_PASSWORD,
            'email': first_user.email
        })
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_AVATAR)
        )