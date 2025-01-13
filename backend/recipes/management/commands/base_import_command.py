import json

from typing import Type, Optional
from django.db.models import Model
from django.core.management.base import BaseCommand


class BaseImportCommand(BaseCommand):
    model: Optional[Type[Model]] = None
    help = 'Импорт данных из JSON-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path', type=str, help='Путь к JSON-файлу с данными'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                new_objects = [
                    self.model(**item)
                    for item in data
                    if not self.model.objects.filter(
                        name=item['name']).exists()
                ]
                self.model.objects.bulk_create(new_objects)
                self.stdout.write(self.style.SUCCESS(
                    f'{len(new_objects)} '
                    f'записей успешно добавлено в {self.model.__name__}.'
                ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка импорта данных: {e}'
            ))
