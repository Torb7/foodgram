from http import HTTPStatus

import pytest

from .helpers import assert_ingredient_response_data, assert_tag_response_data

from recipes.models import Ingredient


@pytest.mark.django_db
def test_anonymous_user_can_get_ingredients(
    api_client, ingredients, ingredients_url
):
    response = api_client.get(ingredients_url)
    assert response.status_code == HTTPStatus.OK

    assert len(response.data) == len(ingredients)
    assert_ingredient_response_data(response.data[0], ingredients[0])


@pytest.mark.django_db
def test_anonymous_user_can_get_ingredients_detail(
    api_client, ingredients, ingredients_detail_url
):
    response = api_client.get(ingredients_detail_url)
    assert response.status_code == HTTPStatus.OK

    assert_ingredient_response_data(response.data, ingredients[0])


@pytest.mark.django_db
def test_ingredients_name_filter(api_client, ingredients_url, ingredients):
    response = api_client.get(ingredients_url, {'name': 'Лук'})
    assert response.status_code == HTTPStatus.OK

    ingredient_from_db = Ingredient.objects.get(name='Лук')

    assert len(response.data) == 1
    assert_ingredient_response_data(response.data[0], ingredient_from_db)


@pytest.mark.django_db
def test_anonymous_user_can_get_tags(api_client, tags, tags_url):
    response = api_client.get(tags_url)
    assert response.status_code == HTTPStatus.OK

    assert len(response.data) == len(tags)
    assert_tag_response_data(response.data[0], tags[0])


@pytest.mark.django_db
def test_anonymous_user_can_get_tags_detail(api_client, tags, tags_detail_url):
    response = api_client.get(tags_detail_url)
    assert response.status_code == HTTPStatus.OK

    assert_tag_response_data(response.data, tags[0])
