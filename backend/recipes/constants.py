MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 254
MAX_LENGTH_FIRST_NAME = 150
MAX_LENGTH_LAST_NAME = 150

MAX_LENGTH_TAG_NAME = 32
MAX_LENGTH_TAG_SLUG = 32

MAX_LENGTH_INGREDIENT_NAME = 128
MAX_LENGTH_INGREDIENT_MEASUREMENT = 64

MAX_LENGTH_RECIPE_NAME = 256

MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 3000
MIN_AMOUNT_INGREDIENT = 1
MAX_AMOUNT_INGREDIENT = 30000

REQUIRED_PATCH_FIELDS = {
    'name': 'Название обязательно.',
    'text': 'Описание обязательно.',
    'cooking_time': 'Время приготовления обязательно.',
    'tags': 'Теги обязательны.',
    'ingredients': 'Ингридиенты обязательны.',
}
