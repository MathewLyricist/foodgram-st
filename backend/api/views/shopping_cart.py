import csv
import io
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.request import Request

from api.serializers import (
    DownloadShoppingCartSerializer,
    ShoppingCartSerializer
)
from api.utils import object_delete, object_update
from recipes.models import Recipe, ShoppingCart


class ShoppingCartMixin:
    """Миксин для работы с корзиной покупок пользователя.
    Обеспечивает добавление/удаление рецептов и выгрузку списка покупок."""

    def get_data(self, request: Request, pk: int) -> dict:
        """Формирует базовые данные для операций с корзиной.

        Args:
            request: Объект HTTP-запроса
            pk: ID рецепта

        Returns:
            Словарь с данными: автор (текущий пользователь) и рецепт
        """
        return {
            'author': request.user,
            'recipe': get_object_or_404(Recipe, id=pk)
        }

    @action(detail=True, methods=['POST'], url_path='shopping_cart')
    def post_shopping_cart(self, request: Request, pk: int):
        """Добавляет рецепт в корзину покупок.

        Args:
            request: Объект HTTP-запроса
            pk: ID рецепта для добавления

        Returns:
            Результат операции добавления (сериализованные данные или ошибка)
        """
        data: dict = self.get_data(request=request, pk=pk)
        serializer = ShoppingCartSerializer(
            data={key: obj.id for key, obj in data.items()},
            context={'request': request}
        )
        return object_update(serializer=serializer)

    @post_shopping_cart.mapping.delete
    def delete_shopping_cart(self, request: Request, pk: int):
        """Удаляет рецепт из корзины покупок.

        Args:
            request: Объект HTTP-запроса
            pk: ID рецепта для удаления

        Returns:
            Результат операции удаления

        Raises:
            NotFound: Если рецепт не найден в корзине
        """
        return object_delete(
            data=self.get_data(request=request, pk=pk),
            error_message='У вас нет данного рецепта в корзине.',
            model=ShoppingCart
        )

    @action(detail=False, methods=['GET'], url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        """Генерирует и возвращает CSV-файл со списком покупок.

        Returns:
            HttpResponse с CSV-файлом, содержащим:
            - Название ингредиента
            - Единицу измерения
            - Необходимое количество

        Файл имеет кодировку cp1251 и формат имени:
        shopping_cart.csv_{user_id}_{timestamp}
        """
        # Сериализация данных корзины
        serializer = DownloadShoppingCartSerializer(
            instance=ShoppingCart.objects.all(),
            many=True, context={'request': request}
        )

        # Формирование имени файла с timestamp
        now = datetime.now()
        formatted_time = now.strftime('%d-%m-%Y_%H_%M_%S')

        # Настройка HTTP-ответа для файла
        response = HttpResponse(content_type='text/csv; charset=cp1251')
        filename = f'shopping_cart.csv_{request.user.id}_{formatted_time}'
        response['Content-Disposition'] = (
            f'attachment; filename="{filename}"'
        )

        # Запись данных в CSV
        csv_buffer = io.TextIOWrapper(response, encoding='cp1251', newline='')
        writer = csv.writer(csv_buffer)

        # Заголовки столбцов
        writer.writerow(['Ингредиент', 'Единица измерения', 'Количество'])

        # Данные ингредиентов (если есть)
        if serializer.data:
            ingredients = serializer.data[0]['ingredients']
            rows = [
                [
                    ingredient['name'],
                    ingredient['measurement_unit'],
                    ingredient['total_amount']
                ] for ingredient in ingredients
            ]
            writer.writerows(rows)

        csv_buffer.flush()
        return response