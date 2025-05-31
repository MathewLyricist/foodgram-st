from core.constants import AUTH
from core.models import PrefixedDBModel


class AuthBaseModel(PrefixedDBModel):
    """Абстрактная базовая модель для сущностей, связанных с пользователями.

    Наследует функциональность PrefixedDBModel и:
    - Устанавливает префикс таблицы из константы AUTH
    - Автоматически назначает новый префикс для таблиц через __init_subclass__
    - Предназначена для использования в качестве родительского класса

    Attributes:
        prefix_name (str): Префикс для именования таблиц в БД (берется из AUTH)

    Meta:
        abstract (bool): Указывает, что это абстрактная модель (не создает таблицу)
    """

    prefix_name = AUTH  # Используем префикс из констант

    class Meta(PrefixedDBModel.Meta):
        """Мета-класс с настройками модели.

        Наследует Meta от PrefixedDBModel и добавляет:
        - abstract = True (модель становится абстрактной)
        """
        abstract = True