from pathlib import Path
from typing import List, Dict, Any

from django.core.management.utils import get_random_secret_key
from environs import Env

# Инициализация окружения
env = Env()
env.read_env()

# Базовые настройки проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Настройки безопасности
SECRET_KEY = env.str('SECRET_KEY', get_random_secret_key())
DEBUG = env.bool('DEBUG', False)
ALLOWED_HOSTS: List[str] = env.str('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Настройки приложений
INSTALLED_APPS: List[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'django_filters',
    'rest_framework.authtoken',
    'djoser',

    'api.apps.ApiConfig',
    'core.apps.CoreConfig',
    'recipes.apps.RecipesConfig',
    'users.apps.UsersConfig',
]

# Промежуточное ПО
MIDDLEWARE: List[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL-конфигурация
ROOT_URLCONF = 'backend.urls'

# Шаблоны
TEMPLATES: List[Dict[str, Any]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'backend.wsgi.application'

# Настройки базы данных
DATABASES: Dict[str, Dict[str, Any]] = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql' if env.bool('USE_PGSQL', False) else 'django.db.backends.sqlite3',
        'NAME': env.str('POSTGRES_DB', 'foodgram') if env.bool('USE_PGSQL', False) else BASE_DIR / 'db.sqlite3',
        'USER': env.str('POSTGRES_USER', 'postgres') if env.bool('USE_PGSQL', False) else '',
        'PASSWORD': env.str('POSTGRES_PASSWORD', '1234567890') if env.bool('USE_PGSQL', False) else '',
        'HOST': env.str('DB_HOST', 'localhost') if env.bool('USE_PGSQL', False) else '',
        'PORT': env.int('DB_PORT', 5432) if env.bool('USE_PGSQL', False) else '',
    }
}

# Валидация паролей
AUTH_PASSWORD_VALIDATORS: List[Dict[str, str]] = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация и время
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'Asia/Yekaterinburg'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статические файлы и медиа
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'collected_static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Модель пользователя
AUTH_USER_MODEL = 'users.User'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки REST Framework
REST_FRAMEWORK: Dict[str, Any] = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': env.int('PAGE_SIZE', 10),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Настройки Djoser
DJOSER: Dict[str, Any] = {
    'HIDE_USERS': False,
    'SERIALIZERS': {
        'user': 'api.serializers.UserSerializer',
        'current_user': 'api.serializers.CurrentUserSerializer',
    },
    'PERMISSIONS': {
        'user_list': ['rest_framework.permissions.AllowAny'],
        'user': ['rest_framework.permissions.AllowAny'],
    }
}

# Лимиты приложения
RECIPES_LIMIT_MAX: int = env.int('RECIPES_LIMIT_MAX', 10)