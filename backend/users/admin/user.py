from typing import Optional

from django.contrib import admin
from django.forms import ModelForm, PasswordInput
from django.http.response import HttpResponse
from rest_framework.request import Request

from recipes.models import RecipeFavorite, ShoppingCart
from users.models.user import User


class UserAdminForm(ModelForm):
    """Кастомная форма пользователя с защитой отображения пароля.

    Наследуется от ModelForm и переопределяет виджет поля пароля
    для его безопасного отображения в админ-панели.
    """

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """Инициализация формы с изменением виджета для поля пароля.

        Args:
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы

        Note:
            Виджет PasswordInput применяется только при создании нового пользователя,
            чтобы избежать отображения хеша пароля.
        """
        super().__init__(*args, **kwargs)
        if not self.instance.pk:  # Только для создания нового пользователя
            self.fields['password'].widget = PasswordInput(
                attrs={'class': 'vTextField'}  # Сохраняем стиль админки
            )


class RecipeFavoriteInline(admin.TabularInline):
    """Inline-админка для управления избранными рецептами пользователя.

    Attributes:
        model: Связь с моделью RecipeFavorite
        autocomplete_fields: Поля с автодополнением
        extra: Количество дополнительных форм
    """

    model = RecipeFavorite
    autocomplete_fields = ['recipe']
    extra = 1  # Количество дополнительных пустых форм


class ShoppingCartInline(admin.TabularInline):
    """Inline-админка для управления корзиной покупок пользователя.

    Attributes:
        model: Связь с моделью ShoppingCart
        autocomplete_fields: Поля с автодополнением
        extra: Количество дополнительных форм
    """

    model = ShoppingCart
    autocomplete_fields = ['recipe']
    extra = 1  # Количество дополнительных пустых форм


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Административный интерфейс для управления пользователями.

    Включает:
    - Управление основными данными пользователей
    - Управление связанными объектами через inline-формы
    - Кастомную логику отображения форм
    """

    form = UserAdminForm  # Используем кастомную форму
    list_display = (
        'username', 'email', 'get_full_name', 'last_login',
        'is_active', 'is_staff'
    )
    search_fields = ('username', 'email')  # Поля для поиска
    list_filter = ('is_active', 'is_staff')  # Фильтры в списке
    ordering = ('id',)  # Сортировка по умолчанию

    readonly_fields = ('date_joined', 'last_login')  # Только для чтения
    exclude = ('groups', 'user_permissions')  # Исключенные поля

    def set_fieldsets(
            self, enabled_password: bool = True, fields: list = []
    ) -> None:
        """Динамически настраивает поля формы редактирования пользователя.

        Args:
            enabled_password: Флаг отображения поля пароля
            fields: Дополнительные поля для отображения
        """
        self.fieldsets = [
            (
                'Персональные данные', {
                'fields': (
                    'username', 'email', 'first_name', 'last_name',
                    *(['password'] if enabled_password else [])
                )
            }
            ),
            (
                'Признаки', {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
            ),
            (
                'Служебная информация', {
                'fields': ('date_joined', *fields)
            }
            )
        ]

    def add_view(
            self, request: Request, extra_content: Optional[dict] = None
    ) -> HttpResponse:
        """Настройка формы добавления нового пользователя."""
        self.set_fieldsets()  # Включаем поле пароля
        return super(UserAdmin, self).add_view(request)

    def change_view(
            self,
            request: Request,
            object_id: int,
            extra_content: Optional[dict] = None
    ) -> HttpResponse:
        """Настройка формы редактирования существующего пользователя."""
        self.set_fieldsets(
            enabled_password=False,  # Отключаем поле пароля
            fields=['last_login']  # Добавляем поле последнего входа
        )
        self.inlines = [RecipeFavoriteInline, ShoppingCartInline]  # Добавляем inline-формы
        return super(UserAdmin, self).change_view(request, object_id)