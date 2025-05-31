from core.constants import COOKBOOK
from core.models import PrefixedDBModel


class CookbookBaseModel(PrefixedDBModel):
    """Заготовка для моделей, связанных с рецептами."""

    prefix_name = COOKBOOK

    class Meta(PrefixedDBModel.Meta):
        abstract = True
