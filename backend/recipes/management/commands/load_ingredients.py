import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.json'

        with path.open(encoding='utf-8') as file:
            ingredients = json.load(file)

        Ingredient.objects.bulk_create(
            Ingredient(
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'],
            )
            for ingredient in ingredients
        )

        self.stdout.write(
            self.style.SUCCESS(f'Загружено ингредиентов: {len(ingredients)}')
        )
