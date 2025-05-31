from http import HTTPStatus
from typing import Any, Optional, Union

from django.db.models import Model
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.utils.general import (
    RESPONSE_EXPECTED_STRUCTURE,
    URL_BAD_REQUEST_ERROR,
    URL_CREATED_ERROR,
    URL_FORBIDDEN_ERROR,
    URL_FOUND_ERROR,
    URL_METHOD_NOT_ALLOWED,
    URL_NO_CONTENT_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    URL_UNAUTHORIZED_ERROR
)


class BaseTest:
    """Базовый класс для тестирования API endpoints."""

    def _url_is_accessible(
            self, response: Response, url: str
    ):
        """
        Внутренний метод для проверки доступности URL.

        Args:
            response: Ответ сервера на запрос
            url: URL, который проверяется на доступность

        Raises:
            AssertionError: если URL недоступен (404 статус)
        """
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )

    def _response_matches_schema(
            self, data: Union[dict, list], response_schema: dict[str, Any]
    ):
        """
        Внутренний метод для валидации структуры ответа по JSON схеме.

        Args:
            data: Данные ответа для проверки
            response_schema: Ожидаемая JSON схема

        Raises:
            AssertionError: если данные не соответствуют схеме
        """
        try:
            validate(
                instance=data,
                schema=response_schema
            )
        except ValidationError:
            assert False, RESPONSE_EXPECTED_STRUCTURE

    def url_is_missing_for_method(
            self, client: APIClient, url: str, method: str
    ):
        """
        Проверяет, что URL недоступен для указанного метода.

        Args:
            client: API клиент для выполнения запроса
            url: URL для проверки
            method: HTTP метод (get, post и т.д.)

        Raises:
            AssertionError: если URL доступен (не возвращает 404)
        """
        response: Response = getattr(client, method)(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )

    def url_requires_authorization(
            self, client: APIClient, url: str, method: str = 'post',
            data: Optional[dict[str, Any]] = None
    ):
        """
        Проверяет, что URL требует авторизации.

        Args:
            client: Неавторизованный API клиент
            url: URL для проверки
            method: HTTP метод (по умолчанию 'post')
            data: Опциональные данные для запроса

        Raises:
            AssertionError: если URL доступен без авторизации
        """
        response: Response = getattr(client, method)(url, data)
        self._url_is_accessible(response=response, url=url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=url)
        )

    def url_bad_request_for_invalid_data(
            self, client: APIClient, url: str, method: str = 'post',
            data: Optional[dict[str, Any]] = None
    ):
        """
        Проверяет обработку невалидных данных (400 статус).

        Args:
            client: API клиент
            url: URL для проверки
            method: HTTP метод (по умолчанию 'post')
            data: Невалидные данные для запроса

        Raises:
            AssertionError: если не возвращается статус 400
        """
        response: Response = getattr(client, method)(url, data)
        self._url_is_accessible(response=response, url=url)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(url=url)
        )

    def url_creates_resource(
            self, *, client: APIClient, url: str, model: Model,
            filters: dict[str, Any], data: Optional[dict[str, Any]] = None,
            response_schema: dict[str, Any]
    ) -> Response:
        """
        Проверяет создание ресурса через API.

        Args:
            client: API клиент
            url: URL для создания ресурса
            model: Модель Django для проверки в БД
            filters: Фильтры для проверки созданного объекта
            data: Данные для создания ресурса
            response_schema: Ожидаемая схема ответа

        Returns:
            Response: Ответ сервера

        Raises:
            AssertionError: если ресурс не создался корректно
        """
        count_in_db = model.objects.count()
        response: Response = client.post(url, data=data)
        self._url_is_accessible(response=response, url=url)
        assert response.status_code == HTTPStatus.CREATED, (
            URL_CREATED_ERROR.format(url=url)
        )

        new_item_in_db = model.objects.filter(**filters)
        assert (
                new_item_in_db.exists()
                and count_in_db + 1 == new_item_in_db.count()
        ), 'Убедитесь, что в БД обновились записи.'

        self._response_matches_schema(
            data=response.json(),
            response_schema=response_schema
        )

        return response

    def url_get_resource(
            self, *, client: Optional[APIClient] = None, url: str,
            response_schema: dict[str, Any], response: Optional[Response] = None
    ):
        """
        Проверяет доступность GET-метода.

        Args:
            client: API клиент (если не передан response)
            url: URL для проверки
            response_schema: Ожидаемая схема ответа
            response: Готовый ответ (если не передан client)

        Raises:
            ValueError: если переданы оба или ни одного из client/response
            AssertionError: если GET-запрос не работает корректно
        """
        if (client and response) or (not client and not response):
            raise ValueError('Нужно передавать либо client, либо response!')
        if client:
            response: Response = client.get(url)
        self._url_is_accessible(response=response, url=url)
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=url)
        )

        self._response_matches_schema(
            data=response.json(),
            response_schema=response_schema
        )

    def url_is_not_allowed_for_method(
            self, client: APIClient, url: str, method: str
    ):
        """
        Проверяет, что метод не разрешен для URL (405 статус).

        Args:
            client: API клиент
            url: URL для проверки
            method: HTTP метод

        Raises:
            AssertionError: если метод разрешен для URL
        """
        response: Response = getattr(client, method)(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            URL_METHOD_NOT_ALLOWED.format(method=method.upper(), url=url)
        )

    def url_put_success_status(
            self, client: APIClient, url: str, model: Model, id_item_update: int,
            field_name: str, new_value: Any, response_schema: dict[str, Any]
    ):
        """
        Проверяет успешное выполнение PUT-запроса.

        Args:
            client: API клиент
            url: URL для обновления
            model: Модель Django для проверки
            id_item_update: ID обновляемого объекта
            field_name: Поле для обновления
            new_value: Новое значение поля
            response_schema: Ожидаемая схема ответа

        Raises:
            AssertionError: если обновление не прошло успешно
        """
        old_item = getattr(model.objects.get(id=id_item_update), field_name)
        response: Response = client.put(url, {field_name: new_value})
        new_item = getattr(model.objects.get(id=id_item_update), field_name)
        self.url_get_resource(
            response=response,
            url=url,
            response_schema=response_schema
        )
        assert old_item != new_item, (
            f'Поле {field_name} в БД должно обновиться.'
        )

    def url_returns_no_content(
            self, response: Response, url: str
    ):
        """
        Проверяет ответ без контента (204 статус).

        Args:
            response: Ответ сервера
            url: URL запроса

        Raises:
            AssertionError: если статус не 204
        """
        self._url_is_accessible(response=response, url=url)
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            URL_NO_CONTENT_ERROR.format(url=url)
        )

    def url_delete_resouce(
            self, client: APIClient, url: str, model: Model, item_id: int
    ):
        """
        Проверяет удаление ресурса.

        Args:
            client: API клиент
            url: URL для удаления
            model: Модель Django для проверки
            item_id: ID удаляемого объекта

        Raises:
            AssertionError: если удаление не прошло успешно
        """
        response: Response = client.delete(url)
        self.url_returns_no_content(response=response, url=url)
        db_items = model.objects.filter(id=item_id)
        assert not db_items, (
            'Убедитесь, что объект удаляется в БД'
        )

    def url_access_denied(
            self, client: APIClient, url: str, method: str,
            body: Optional[dict[str, Any]] = None
    ):
        """
        Проверяет ограничение доступа (403 статус).

        Args:
            client: API клиент
            url: URL для проверки
            method: HTTP метод
            body: Тело запроса

        Raises:
            AssertionError: если доступ не запрещен
        """
        response: Response = getattr(client, method)(url, body)
        self._url_is_accessible(response=response, url=url)
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            URL_FORBIDDEN_ERROR.format(method=method, url=url)
        )

    def url_redirects_with_found_status(
            self, client: APIClient, url: str, expected_redirect_url: str
    ):
        """
        Проверяет редирект (302 статус).

        Args:
            client: API клиент
            url: Исходный URL
            expected_redirect_url: Ожидаемый URL редиректа

        Raises:
            AssertionError: если редирект не происходит или неверный
        """
        response: Response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND, (
            URL_FOUND_ERROR.format(method='patch', url=url)
        )
        redirect_url = response.headers.get('Location')
        assert redirect_url == expected_redirect_url, (
            f'Проверьте, что адрес `{url}` перенаправляет на '
            f'`{expected_redirect_url}`. На текущий момент перенаправляет на '
            f'`{redirect_url}`.'
        )

    def url_reponse_count_matches_db_count(
            self, data: dict, model: Model, filters: dict[str, Any]
    ):
        """
        Проверяет соответствие количества объектов в ответе и БД.

        Args:
            data: Ответ API
            model: Модель Django для проверки
            filters: Фильтры для выборки из БД

        Raises:
            AssertionError: если количества не совпадают
        """
        count_subscribe_DB = (
            model.objects.filter(**filters).distinct()
        )
        assert (
                count_subscribe_DB.exists()
                and len(data) == count_subscribe_DB.count()
        ), 'Убедитесь, что отобразились все записи.'

    def url_limits_results_count(
            self, data: dict[str, Any], model: Model, filters: dict[str, Any],
            limit: int
    ):
        """
        Проверяет ограничение количества результатов (не для пагинации).

        Args:
            data: Ответ API
            model: Модель Django для проверки
            filters: Фильтры для выборки из БД
            limit: Ожидаемое ограничение

        Raises:
            AssertionError: если ограничение не работает
        """
        count_in_DB = model.objects.filter(**filters).distinct().count()
        expected_count = limit if limit < count_in_DB else count_in_DB
        assert len(data) == expected_count, (
            'Должна быть возможность изменить количество отображаемых данных'
        )

    def url_pagination_results(
            self, data: dict[str, Any], limit: int
    ):
        """
        Проверяет работу пагинации.

        Args:
            data: Ответ API
            limit: Ожидаемый лимит на странице

        Raises:
            AssertionError: если пагинация не работает
        """
        response_count: int = data.get('count', 0)
        response_results: list = data.get('results', [])
        expected_count = limit if limit < response_count else response_count
        assert len(response_results) == expected_count, (
            'Убедитесь что работает пагинация.'
        )

    def url_filters_by_query_parameters(
            self, response: Response, model: Model, filters: dict[str, Any],
            limit: Optional[int] = None
    ):
        """
        Проверяет фильтрацию по query-параметрам.

        Args:
            response: Ответ сервера
            model: Модель Django для проверки
            filters: Фильтры для сравнения
            limit: Опциональный лимит

        Raises:
            AssertionError: если фильтрация не работает
        """
        count_in_DB = model.objects.filter(**filters).distinct().count()
        data: dict = response.json()
        response_count = len(data)
        if limit:
            expected_count_results = (
                count_in_DB if count_in_DB < limit else limit
            )
        else:
            expected_count_results = count_in_DB
        assert count_in_DB == expected_count_results, (
            'Убедитесь, что фильтрация работает корректно. Ожидалось '
            f'{count_in_DB} элементов, пришло {response_count}.'
        )

    def check_db_no_changes_made(
            self, client: APIClient, url: str, model: Model
    ):
        """
        Проверяет, что в БД не было изменений.

        Args:
            client: API клиент
            url: URL запроса
            model: Модель Django для проверки

        Raises:
            AssertionError: если в БД были изменения
        """
        count_in_db = model.objects.count()
        self.url_bad_request_for_invalid_data(client=client, url=url)
        new_count_in_db = model.objects.count()
        assert count_in_db == new_count_in_db, (
            'Убедитесь, что данные в БД не изменились.'
        )