import base64

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from recipes.models import Recipe, Tag, Ingredient, RecipeIngredients


@pytest.fixture
def user(django_user_model, user_password):
    return django_user_model.objects.create_user(
        username='test',
        email='vpupkin@yandex.ru',
        first_name='Вася',
        last_name='Иванов',
        password=user_password,
    )


@pytest.fixture
def another_user(django_user_model, user_password):
    return django_user_model.objects.create_user(
        username='another_user',
        email='another_user@yandex.ru',
        first_name='Test',
        last_name='Test',
        password=user_password,
    )


@pytest.fixture
def subscribed_user(user, another_user):
    user.following.add(another_user)

    return user


@pytest.fixture
def user_password():
    return 'testpassword123'


@pytest.fixture
def user_data(user_password):
    return {
        'email': 'test@test.ru',
        'username': 'test',
        'first_name': 'test',
        'last_name': 'test',
        'password': user_password,
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_auth_client(api_client, login_url, user, user_password):
    data = {'email': user.email, 'password': user_password}

    response = api_client.post(login_url, data=data)

    token = response.data['auth_token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    return api_client


@pytest.fixture
def api_not_author_client(api_client, login_url, another_user, user_password):
    data = {'email': another_user.email, 'password': user_password}

    response = api_client.post(login_url, data=data)

    token = response.data['auth_token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    return api_client


@pytest.fixture
def login_url():
    return reverse('login')


@pytest.fixture
def logout_url():
    return reverse('logout')


@pytest.fixture
def signup_url():
    return reverse('users-list')


@pytest.fixture
def users_url():
    return reverse('users-list')


@pytest.fixture
def users_detail_url(user):
    return reverse('users-detail', args=(user.pk,))


@pytest.fixture
def users_me_url():
    return reverse('users-me')


@pytest.fixture
def avatar_url():
    return reverse('users-avatar')


@pytest.fixture
def avatar_image():
    return (
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
        'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQIm'
        'WNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
    )


@pytest.fixture
def subscriptions_url():
    return reverse('users-subscriptions')


@pytest.fixture
def subscribe_url(another_user):
    return reverse('users-subscribe', args=(another_user.pk,))


@pytest.fixture
def ingredients():
    return (
        Ingredient.objects.create(name='Картофель', measurement_unit='г'),
        Ingredient.objects.create(name='Лук', measurement_unit='г'),
    )


@pytest.fixture
def ingredients_update():
    return (
        Ingredient.objects.create(name='Соль', measurement_unit='г'),
        Ingredient.objects.create(name='Сахар', measurement_unit='г'),
    )


@pytest.fixture
def tags():
    return (
        Tag.objects.create(name='Завтрак', slug='breakfast'),
        Tag.objects.create(name='Обед', slug='lunch'),
        Tag.objects.create(name='Ужин', slug='dinner'),
    )


@pytest.fixture
def tags_update():
    return (
        Tag.objects.create(name='Суп', slug='soup'),
        Tag.objects.create(name='Выпечка', slug='bakery'),
    )


@pytest.fixture
def recipe_image():
    return (
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAA'
        'ACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNo'
        'AAAAggCByxOyYQAAAABJRU5ErkJggg=='
    )


@pytest.fixture
def recipe_image_file(recipe_image):
    return SimpleUploadedFile(
        name='test.png',
        content=base64.b64decode(recipe_image.split(',')[1]),
        content_type='image/png',
    )


@pytest.fixture
def recipe_data(recipe_image, ingredients, tags):
    return {
        'ingredients': [
            {'id': ingredient.id, 'amount': 10} for ingredient in ingredients
        ],
        'tags': [tag.id for tag in tags],
        'name': 'recipe_test',
        'text': 'recipe_test',
        'cooking_time': 1,
        'image': recipe_image,
    }


@pytest.fixture
def recipe(user, recipe_image_file, ingredients, tags):
    recipe = Recipe.objects.create(
        author=user,
        name='Тестовый рецепт',
        text='Текст рецепта',
        cooking_time=10,
        image=recipe_image_file,
    )

    recipe.tags.set(tags)
    RecipeIngredients.objects.bulk_create(
        RecipeIngredients(recipe=recipe, ingredient=ingredient, amount=22)
        for ingredient in ingredients
    )

    return recipe


@pytest.fixture
def recipe_data_update(recipe_image, ingredients_update, tags_update):
    return {
        'ingredients': [
            {'id': ingredient.id, 'amount': 10}
            for ingredient in ingredients_update
        ],
        'tags': [tag.id for tag in tags_update],
        'name': 'recipe_test_update',
        'text': 'recipe_test_update',
        'cooking_time': 2,
        'image': recipe_image,
    }


@pytest.fixture
def recipes_for_filters(
    user, another_user, recipe_image_file, ingredients, tags
):
    recipe_1 = Recipe.objects.create(
        author=user,
        name='Тестовый рецепт',
        text='Текст рецепта',
        cooking_time=10,
        image=recipe_image_file,
    )
    recipe_1.tags.add(tags[0])
    RecipeIngredients.objects.bulk_create(
        RecipeIngredients(recipe=recipe_1, ingredient=ingredient, amount=22)
        for ingredient in ingredients
    )

    recipe_2 = Recipe.objects.create(
        author=user,
        name='Тестовый рецепт',
        text='Текст рецепта',
        cooking_time=10,
        image=recipe_image_file,
    )
    recipe_2.tags.add(tags[1])
    RecipeIngredients.objects.bulk_create(
        RecipeIngredients(recipe=recipe_2, ingredient=ingredient, amount=22)
        for ingredient in ingredients
    )

    recipe_3 = Recipe.objects.create(
        author=another_user,
        name='Тестовый рецепт',
        text='Текст рецепта',
        cooking_time=10,
        image=recipe_image_file,
    )
    recipe_3.tags.add(tags[2])
    RecipeIngredients.objects.bulk_create(
        RecipeIngredients(recipe=recipe_3, ingredient=ingredient, amount=22)
        for ingredient in ingredients
    )

    user.favorite_recipes.add(recipe_1, recipe_2)
    user.shopping_cart.add(recipe_1, recipe_2)

    return recipe_1, recipe_2, recipe_3


@pytest.fixture
def recipes_for_pagination(user):
    return [
        Recipe.objects.create(
            name=f'Recipe {i}', text=f'Text {i}', cooking_time=1, author=user
        )
        for i in range(1, 5)
    ]


@pytest.fixture
def recipes_url():
    return reverse('recipes-list')


@pytest.fixture
def recipes_detail_url(recipe):
    return reverse('recipes-detail', args=(recipe.pk,))


@pytest.fixture
def recipes_favorite_url(recipe):
    return reverse('recipes-favorite', args=(recipe.pk,))


@pytest.fixture
def recipes_shopping_cart_url(recipe):
    return reverse('recipes-shopping-cart', args=(recipe.pk,))
