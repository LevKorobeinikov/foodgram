import csv

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from foodgram import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv-файла в модель Ingredient в базе данных'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        success_count = 0
        print('Загрузка данных')
        with open(
                f'{settings.BASE_DIR}/data/ingredients.csv',
                'r',
                encoding='utf-8',
        ) as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                name_csv = 0
                unit_csv = 1
                try:
                    obj, created = Ingredient.objects.get_or_create(
                        name=row[name_csv],
                        measurement_unit=row[unit_csv],
                    )
                    if created:
                        success_count += 1
                    if not created:
                        print(f'Ингредиент {obj} уже существует в базе данных')
                except IntegrityError as err:
                    print(f'Ошибка в строке {row}: {err}')
        print(f'{success_count} записей было импортировано из csv-файла.')
