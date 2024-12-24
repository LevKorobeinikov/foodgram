import json

from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импортирует теги из JSON-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path', type=str, help='Путь к JSON-файлу с тегами'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tags = []
                for item in json.load(file):
                    tags.append(Tag(
                        name=item.get('name'), slug=item.get('slug')
                    ))
                Tag.objects.bulk_create(tags)
                self.stdout.write(self.style.SUCCESS(
                    'Теги успешно добавлены.'
                ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Тэги уже сущестуют: {e}'
            ))
