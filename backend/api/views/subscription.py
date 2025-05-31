from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from api.serializers import (
    SubscriptionChangedSerializer,
    SubscriptionGetSerializer
)
from api.utils import object_delete, object_update
from users.models import Subscription, User


class SubscriptionMixin:
    """Миксин для управления подписками пользователей.
    Обеспечивает функционал подписки/отписки и просмотра подписок."""

    def get_data(self, request: Request, id: int) -> dict:
        """Подготавливает базовые данные для операций с подписками.

        Args:
            request: Объект запроса
            id: ID пользователя, на которого подписываются/отписываются

        Returns:
            Словарь с данными: текущий пользователь и целевой пользователь
        """
        return {
            'user': request.user,
            'author_recipe': get_object_or_404(User, id=id)
        }

    @action(['GET'], detail=False, url_path='subscriptions')
    def subscriptions(self, request: Request):
        """Получает список всех подписок текущего пользователя.

        Returns:
            Ответ с пагинированным списком подписок в формате JSON
        """
        user = request.user
        queryset = User.objects.filter(authors__user=user)
        pages = self.paginate_queryset(queryset)

        serializer = SubscriptionGetSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def post_subscribe(self, request: Request, id: int):
        """Обрабатывает запрос на подписку на пользователя.

        Args:
            request: Объект запроса
            id: ID пользователя для подписки

        Returns:
            Результат операции подписки (успех/ошибка)
        """
        data: dict = self.get_data(request=request, id=id)
        serializer = SubscriptionChangedSerializer(
            data={key: obj.id for key, obj in data.items()},
            context={'request': request}
        )
        return object_update(serializer=serializer)

    @post_subscribe.mapping.delete
    def delete_subscribe(self, request: Request, id: int):
        """Обрабатывает запрос на отписку от пользователя.

        Args:
            request: Объект запроса
            id: ID пользователя для отписки

        Returns:
            Результат операции отписки (успех/ошибка)

        Raises:
            NotFound: Если подписка не найдена
        """
        return object_delete(
            data=self.get_data(request=request, id=id),
            error_message='У вас нет данного пользователя в подписчиках.',
            model=Subscription
        )