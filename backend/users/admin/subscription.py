from typing import Optional

from django.contrib import admin
from django.http.response import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from rest_framework.request import Request

from users.models.subscription import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления подписками пользователей.

    Позволяет администраторам:
    - Просматривать список подписок
    - Искать подписки по имени автора или подписчика
    - Быстро переходить к редактированию связанных пользователей
    - Управлять обязательными полями подписки
    """

    # Настройки отображения списка подписок
    list_display = ('id', 'get_author_recipe', 'get_user', 'created_at')
    search_fields = ('author_recipe__username', 'user__username')
    autocomplete_fields = ('author_recipe', 'user')
    ordering = ('id',)
    readonly_fields = ('created_at',)

    # Группировка полей в форме редактирования
    required_block = (
        'Обязательные данные', {
        'fields': ('author_recipe', 'user')
    }
    )

    def add_view(
            self, request: Request, extra_content: Optional[dict] = None
    ) -> HttpResponse:
        """Настройка отображения формы добавления новой подписки."""
        self.fieldsets = [self.required_block]
        return super(SubscriptionAdmin, self).add_view(request)

    def change_view(
            self,
            request: Request,
            object_id: int,
            extra_content: Optional[dict] = None
    ) -> HttpResponse:
        """Настройка отображения формы редактирования существующей подписки."""
        self.fieldsets = [
            self.required_block,
            (None, {'fields': ('created_at',)})
        ]
        return super(SubscriptionAdmin, self).change_view(request, object_id)

    def get_author_recipe(self, obj: Subscription) -> str:
        """Генерирует HTML-ссылку на страницу редактирования автора рецепта.

        Args:
            obj: Объект подписки

        Returns:
            HTML-ссылка на страницу редактирования автора
        """
        url = reverse('admin:users_user_change', args=[obj.author_recipe.id])
        return format_html(
            '<a href="{}">{}</a>', url, obj.author_recipe.username
        )

    def get_user(self, obj: Subscription) -> str:
        """Генерирует HTML-ссылку на страницу редактирования подписчика.

        Args:
            obj: Объект подписки

        Returns:
            HTML-ссылка на страницу редактирования подписчика
        """
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    # Устанавливаем читаемые названия для колонок
    get_author_recipe.short_description = 'Автор рецепта'
    get_user.short_description = 'Подписчик'