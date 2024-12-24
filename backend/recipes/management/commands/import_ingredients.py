import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из JSON-файла в базу данных'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path', type=str, help='Путь к JSON-файлу с ингредиентами'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                ingredients = []
                for item in data:
                    ingredients.append(
                        Ingredient(
                            name=item.get('name'),
                            measurement_unit=item.get('measurement_unit')
                        )
                    )
                Ingredient.objects.bulk_create(ingredients)
                self.stdout.write(self.style.SUCCESS(
                    'Ингредиенты успешно добавлены.'
                ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f'Игредиент уже существует:{e}'
            ))
