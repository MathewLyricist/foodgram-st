import pytest
from django.contrib.auth import get_user_model
from django.db.models import Model
from rest_framework.test import APIClient

from tests.utils.user import (
    FIRST_VALID_USER,
    SECOND_VALID_USER,
    THIRD_VALID_USER
)

User = get_user_model()

def create_user(django_user_model, user_data) -> Model:
    """Создает пользователя через модель Django."""
    return django_user_model.objects.create_user(**user_data)

def get_user_token(user: User, password: str) -> dict[str, str]:
    """Получает токен авторизации для пользователя."""
    client = APIClient()
    response = client.post(
        '/api/auth/token/login/',
        {'email': user.email, 'password': password}
    )
    return {'auth_token': response.data['auth_token']}

def authorized_client(token: dict) -> APIClient:
    """Создает авторизованный клиент API с токеном."""
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token["auth_token"]}')
    return client

# Базовые фикстуры клиента и пользователей
@pytest.fixture
def api_client() -> APIClient:
    return APIClient()

@pytest.fixture
def first_user(django_user_model: Model) -> Model:
    return create_user(django_user_model, FIRST_VALID_USER)

@pytest.fixture
def second_user(django_user_model: Model) -> Model:
    return create_user(django_user_model, SECOND_VALID_USER)

@pytest.fixture
def third_user(django_user_model: Model) -> Model:
    return create_user(django_user_model, THIRD_VALID_USER)

# Групповые фикстуры
@pytest.fixture
def all_user(first_user: Model, second_user: Model, third_user: Model) -> list:
    return [first_user, second_user, third_user]

# Фикстуры токенов
@pytest.fixture
def first_user_token(first_user: Model) -> dict:
    return get_user_token(first_user, FIRST_VALID_USER['password'])

@pytest.fixture
def second_user_token(second_user: Model) -> dict:
    return get_user_token(second_user, SECOND_VALID_USER['password'])

@pytest.fixture
def third_user_token(third_user: Model) -> dict:
    return get_user_token(third_user, THIRD_VALID_USER['password'])

# Фикстуры авторизованных клиентов
@pytest.fixture
def first_user_authorized_client(first_user_token: dict) -> APIClient:
    return authorized_client(first_user_token)

@pytest.fixture
def second_user_authorized_client(second_user_token: dict) -> APIClient:
    return authorized_client(second_user_token)

@pytest.fixture
def third_user_authorized_client(third_user_token: dict) -> APIClient:
    return authorized_client(third_user_token)