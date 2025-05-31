# Числовые константы
NOT_EXISTING_ID = 9786  # ID, который гарантированно не существует в БД

# Сообщения об ошибках HTTP-статусов
URL_BAD_REQUEST_ERROR = (
    'POST-запрос на `{url}` без обязательных данных должен возвращать статус 400.'
)
URL_CREATED_ERROR = (
    'POST-запрос к `{url}` с корректными данными должен возвращать статус 201.'
)
URL_FORBIDDEN_ERROR = (
    'Метод `{method}` для `{url}` должен быть доступен только автору.'
)
URL_METHOD_NOT_ALLOWED = (
    'Метод `{method}` не должен быть разрешен для `{url}`.'
)
URL_NOT_FOUND_ERROR = (
    'Эндпоинт `{url}` не найден. Проверьте настройки маршрутизации.'
)
URL_NO_CONTENT_ERROR = (
    'POST-запрос к `{url}` должен возвращать статус 204 при успехе.'
)
URL_OK_ERROR = (
    'POST-запрос к `{url}` должен возвращать статус 200 при успехе.'
)
URL_UNAUTHORIZED_ERROR = (
    'POST-запрос к `{url}` без авторизации должен возвращать статус 401.'
)
URL_FOUND_ERROR = (
    'GET-запрос к `{url}` должен возвращать статус 302 при редиректе.'
)

# Общие сообщения об ошибках
RESPONSE_EXPECTED_STRUCTURE = (
    'Ответ API не соответствует ожидаемой структуре данных.'
)

# Конфигурация HTTP-методов
CHANGE_METHOD = {
    'post': {'url': '{url}', 'detail': False},  # Для коллекций
    'put': {'url': '{url}', 'detail': True},  # Для конкретного объекта
    'patch': {'url': '{url}', 'detail': True},  # Для частичного обновления
    'delete': {'url': '{url}', 'detail': True}  # Для удаления
}


def installation_method_urls(
        url: str,
        url_detail: str,
        dict_method_urls: dict[str, dict]
) -> dict[str, dict]:
    """Форматирует URL-адреса для разных HTTP-методов."""
    result = dict_method_urls.copy()
    for method_info in result.values():
        method_info['url'] = method_info['url'].format(
            url=url_detail if method_info['detail'] else url
        )
    return result