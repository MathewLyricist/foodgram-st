import csv
import json
from typing import Dict, List, Any

from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import termcolors
from django.apps import apps


class Command(BaseCommand):
    """Команда для управления загрузкой начальных данных в БД.

    Поддерживает загрузку данных из CSV и JSON файлов в указанные модели.
    """
    # Конфигурация данных
    DATA_CONFIG = [
        {
            'file_name': 'ingredients',
            'model': 'recipes.Ingredient',
            'fields': ['name', 'measurement_unit'],
            'type': 'csv'
        }
    ]

    help = 'Загрузка данных из CSV и JSON файлов в указанные модели'

    def __init__(self) -> None:
        """Инициализация команды с кастомными стилями вывода."""
        super().__init__()
        self.style.NOTICE = termcolors.make_style(fg='cyan', opts=('bold',))

    def add_arguments(self, parser):
        parser.add_argument(
            'file_type',
            type=str,
            nargs='?',
            default='all',
            help='Тип файла для загрузки: csv, json, или all (все файлы)'
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        file_type: str = kwargs['file_type'].lower()
        self._validate_file_type(file_type)
        self._process_data_entries(file_type)

    def _validate_file_type(self, file_type: str):
        valid_file_types = {'csv', 'json', 'all'}
        if file_type not in valid_file_types:
            self.stderr.write(self.style.ERROR(
                f'Неверный тип: {file_type}. Доступны: csv, json, all.'
            ))
            raise ValueError("Неподдерживаемый тип файла")

    def _process_data_entries(self, file_type: str):
        try:
            for config in self.DATA_CONFIG:
                if self._should_skip_config(config, file_type):
                    continue

                self._process_single_config(config)

            self.stdout.write(self.style.SUCCESS(
                'Все данные успешно загружены'
            ))

        except Exception as error:
            self.stderr.write(self.style.ERROR(
                f'Критическая ошибка загрузки: {error}'
            ))
            raise

    def _should_skip_config(self, config: Dict, file_type: str) -> bool:
        if file_type != 'all' and config['type'] != file_type:
            self.stderr.write(self.style.WARNING(
                f'Пропуск {config["file_name"]} - не соответствует типу {file_type}'
            ))
            return True
        return False

    def _process_single_config(self, config: Dict):
        file_path = f'data/{config["file_name"]}.{config["type"]}'
        model = apps.get_model(config['model'])

        self.stdout.write(self.style.NOTICE(
            f'Загрузка {file_path} в модель {config["model"]}'
        ))

        if config['type'] == 'csv':
            self._load_csv(file_path, model, config['fields'])
        elif config['type'] == 'json':
            self._load_json(file_path, model, config['fields'])

    def _load_csv(self, file_path: str, model: models.Model, fields: List[str]):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) != len(fields):
                    continue

                row_data = dict(zip(fields, row))
                self._update_or_create_model(model, fields[0], row_data)

    def _load_json(self, file_path: str, model: models.Model, fields: List[str]):
        with open(file_path, mode='r', encoding='utf-8') as file:
            json_data = json.load(file)
            for item in json_data:
                filtered_data = {
                    field: item[field]
                    for field in fields
                    if field in item
                }
                self._update_or_create_model(model, fields[0], filtered_data)

    def _update_or_create_model(
            self,
            model: models.Model,
            key_field: str,
            data: Dict[str, Any]
    ):
        """Данная функция создает или обновляет запись в модели."""
        model.objects.update_or_create(
            **{key_field: data[key_field]},
            defaults=data
        )