from django.db.models import Model
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

MODIFY_METHODS = ('PUT', 'PATCH', 'DELETE')


class ReadOnly(BasePermission):
    """Разрешает только безопасные методы запросов (GET, HEAD, OPTIONS)."""

    def has_permission(self, request: Request, view: GenericViewSet) -> bool:
        """Проверяет, является ли метод запроса безопасным."""
        return request.method in SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """Проверяет права доступа - разрешает либо автору, либо только чтение."""

    def has_permission(self, request: Request, view: GenericViewSet) -> bool:
        """Проверяет общие права доступа."""
        return (
                request.method in SAFE_METHODS or
                request.user and request.user.is_authenticated
        )

    def has_object_permission(
            self,
            request: Request,
            view: GenericViewSet,
            obj: Model
    ) -> bool:
        """Проверяет права доступа к конкретному объекту."""
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user