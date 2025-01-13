from recipes.models import Tag
from recipes.management.commands.base_import_command import BaseImportCommand


class Command(BaseImportCommand):
    help = 'Импортирует теги из JSON-файла в базу данных'
    model = Tag
