from re import sub as re_sub
from uuid import uuid4

from core.constants import MAX_LENGTH_SHORT_LINK


def generate_short_link() -> str:
    """Генерирует короткую уникальную ссылку на основе UUID4."""

    return uuid4().hex[:MAX_LENGTH_SHORT_LINK]


def to_snake_case(text: str) -> str:
    """Преобразовывает CamelCase в snake_case."""

    return re_sub(r'(?<!^)(?=[A-Z])', '_', text).lower()
