from typing import Optional, List, Dict, Any

from rest_framework.exceptions import ValidationError


class SubscribeUniqueValidator:
    """Проверяет, что пользователь не пытается подписаться на самого себя."""

    default_message = 'Невозможно подписаться на самого себя'

    def __init__(self, fields: List[str], message: Optional[str] = None):
        """Инициализация валидатора."""
        self.fields = fields
        self.message = message or self.default_message

    def __call__(self, attrs: Dict[str, Any]) -> None:
        """Выполняет проверку валидации."""
        user = attrs.get(self.fields[0])
        author = attrs.get(self.fields[1])

        if user == author:
            raise ValidationError(
                detail={'errors': self.message},
                code='self_subscription'
            )


class UniqueDataInManyFieldValidator:
    """Проверяет уникальность значений в списке объектов или словарей."""

    def __init__(
            self,
            *,
            field: str,
            message: str,
            is_dict: bool = False,
            key: Optional[str] = None
    ):
        """Инициализация валидатора."""
        self.field = field
        self.message = message
        self.is_dict = is_dict

        if is_dict and not key:
            raise ValueError('Требуется передать поле key для поиска')
        self.search_field = key

    def __call__(self, value: Dict[str, Any]) -> None:
        """Выполняет проверку уникальности."""
        data_list = value.get(self.field, [])

        unique_values = {
            item[self.search_field] if self.is_dict else item
            for item in data_list
        }

        # Проверяем на дубликаты
        if len(data_list) != len(unique_values):
            raise ValidationError(
                detail={'errors': self.message},
                code='duplicate_values'
            )