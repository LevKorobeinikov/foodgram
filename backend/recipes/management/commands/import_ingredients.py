from recipes.models import Ingredient
from recipes.management.commands.base_import_command import BaseImportCommand


class Command(BaseImportCommand):
    help = 'Импортирует ингредиенты из JSON-файла в базу данных'
    model = Ingredient
