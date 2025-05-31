from tests.utils.user import RESPONSE_SCHEMA_USER

# Тестовое изображение в base64 (минимальный валидный PNG)
TEST_IMAGE = (
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
    'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQV'
    'QImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
)

# API endpoints
RECIPES_URL = '/api/recipes/'                   # Список рецептов
RECIPE_DETAIL_URL = '/api/recipes/{id}/'        # Детали рецепта
RECIPE_FRONTEND_URL = '/recipes/{id}/'          # Фронтенд URL
RECIPE_SHORTLINK_URL = '/api/recipes/{id}/get-link/'  # Генерация короткой ссылки
SHORTLINK_REDIRECT_URL = '/s/{uuid}/'          # Редирект по короткой ссылке

# Тестовые данные
SAMPLE_INGREDIENTS = [
    {'id': 1, 'amount': 10},
    {'id': 2, 'amount': 20}
]
SAMPLE_NAME = 'Тестовый рецепт'
SAMPLE_DESCRIPTION = 'Описание тестового рецепта'
SAMPLE_COOKING_TIME = 30  # минуты

# Валидные данные для обновления рецепта
VALID_UPDATE_DATA = {
    'ingredients': [{'id': 1, 'amount': 15}],
    'image': TEST_IMAGE,
    'name': 'Обновленный тестовый рецепт',
    'text': 'Новое описание рецепта',
    'cooking_time': 25
}

# Невалидные данные для POST/PATCH запросов
INVALID_REQUEST_DATA = {
    # Общие для POST и PATCH
    'missing_ingredients': {
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'empty_ingredients_list': {
        'ingredients': [],
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'invalid_image': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': '',
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'empty_name': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': '',
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'empty_description': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': '',
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'invalid_cooking_time_type': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': ''
    },
    'nonexistent_ingredient': {
        'ingredients': [{'id': 9999, 'amount': 25}],
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'duplicate_ingredients': {
        'ingredients': [
            {'id': 1, 'amount': 10},
            {'id': 1, 'amount': 20},
        ],
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'invalid_ingredient_amount': {
        'ingredients': [{'id': 1, 'amount': 0}],
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'invalid_cooking_time_value': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': 0
    },
    'name_too_long': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': 'Очень длинное название рецепта...' * 10,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    }
}

# Специфичные для POST запросов ошибки
POST_ONLY_INVALID_DATA = {
    'missing_image': {
        'ingredients': SAMPLE_INGREDIENTS,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'missing_name': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'text': SAMPLE_DESCRIPTION,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'missing_description': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'cooking_time': SAMPLE_COOKING_TIME
    },
    'missing_cooking_time': {
        'ingredients': SAMPLE_INGREDIENTS,
        'image': TEST_IMAGE,
        'name': SAMPLE_NAME,
        'text': SAMPLE_DESCRIPTION
    }
}

# JSON-схемы для валидации ответов
SHORT_RECIPE_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'number'},
        'name': {'type': 'string'},
        'image': {'type': 'string'},
        'cooking_time': {'type': 'number'}
    },
    'required': ['id', 'name', 'image', 'cooking_time'],
    'additionalProperties': False
}

SHORTLINK_SCHEMA = {
    'type': 'object',
    'properties': {
        'short-link': {'type': 'string'}
    },
    'required': ['short-link'],
    'additionalProperties': False
}

RECIPE_DETAIL_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'number'},
        'author': RESPONSE_SCHEMA_USER,
        'ingredients': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'number'},
                    'name': {'type': 'string'},
                    'measurement_unit': {'type': 'string'},
                    'amount': {'type': 'number'}
                },
                'required': ['id', 'name', 'measurement_unit', 'amount'],
                'additionalProperties': False
            }
        },
        'is_favorited': {'type': 'boolean'},
        'is_in_shopping_cart': {'type': 'boolean'},
        'name': {'type': 'string'},
        'image': {'type': 'string'},
        'text': {'type': 'string'},
        'cooking_time': {'type': 'number'}
    },
    'required': [
        'id', 'author', 'ingredients', 'is_favorited',
        'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
    ],
    'additionalProperties': False
}

RECIPE_LIST_SCHEMA = {
    'type': 'object',
    'required': ['count', 'next', 'previous', 'results'],
    'additionalProperties': False,
    'properties': {
        'count': {'type': 'number'},
        'next': {'type': ['string', 'null']},
        'previous': {'type': ['string', 'null']},
        'results': {
            'type': 'array',
            'items': RECIPE_DETAIL_SCHEMA
        }
    }
}