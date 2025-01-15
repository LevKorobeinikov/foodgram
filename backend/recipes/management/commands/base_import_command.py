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
                ]
                added_ingredients = self.model.objects.bulk_create(
                    new_objects,
                    ignore_conflicts=True
                )
                self.stdout.write(self.style.SUCCESS(
                    f'Успешно добавлены в {self.model.__name__} - '
                    f'{len(added_ingredients)} записей из {len(new_objects)}.'
                ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Ошибка импорта данных из файла {file_path}: {e}'
            ))
