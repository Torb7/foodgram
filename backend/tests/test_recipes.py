from http import HTTPStatus

import pytest

from .helpers import (
    assert_recipe_response_data,
    assert_recipe_matches_data,
    assert_recipe_unchanged,
    assert_recipe_ids,
)
from recipes.models import Recipe


@pytest.mark.django_db
def test_anonymous_user_can_get_recipes(api_client, recipe, recipes_url):
    response = api_client.get(recipes_url)
    assert response.status_code == HTTPStatus.OK

    assert response.data['count'] == 1
    assert_recipe_response_data(
        response.data['results'][0],
        recipe,
        expected_is_favorited=False,
        expected_is_in_shopping_cart=False,
    )


@pytest.mark.django_db
def test_anonymous_user_can_get_recipes_detail(
    api_client, recipe, recipes_detail_url
):
    response = api_client.get(recipes_detail_url)
    assert response.status_code == HTTPStatus.OK

    assert_recipe_response_data(
        response.data,
        recipe,
        expected_is_favorited=False,
        expected_is_in_shopping_cart=False,
    )


@pytest.mark.django_db
def test_anonymous_user_cant_create_recipe(
    api_client, recipe_data, recipes_url
):
    response = api_client.post(recipes_url, recipe_data, format='json')

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert Recipe.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_create_recipe(
    api_auth_client, recipe_data, recipes_url, user, tags
):
    response = api_auth_client.post(recipes_url, recipe_data, format='json')
    assert response.status_code == HTTPStatus.CREATED

    assert Recipe.objects.count() == 1
    recipe = Recipe.objects.get(pk=response.data['id'])

    assert_recipe_matches_data(response.data, recipe, user, tags)

    assert_recipe_response_data(
        response.data,
        recipe,
        expected_is_favorited=False,
        expected_is_in_shopping_cart=False,
    )


@pytest.mark.django_db
def test_anonymous_user_cant_edit_recipe(
    api_client, recipe_data, recipes_detail_url, recipe
):
    response = api_client.patch(recipes_detail_url, recipe_data)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    recipe_from_db = Recipe.objects.get(pk=recipe.pk)
    assert_recipe_unchanged(recipe_from_db, recipe)


@pytest.mark.django_db
def test_author_can_edit_recipe(
    api_auth_client, recipe_data_update, recipes_detail_url, user, tags_update
):

    response = api_auth_client.patch(
        recipes_detail_url, recipe_data_update, format='json'
    )
    assert response.status_code == HTTPStatus.OK

    recipe_from_db = Recipe.objects.get(pk=response.data['id'])

    assert_recipe_matches_data(
        response.data, recipe_from_db, user, tags_update
    )

    assert_recipe_response_data(
        response.data,
        recipe_from_db,
        expected_is_favorited=False,
        expected_is_in_shopping_cart=False,
    )


@pytest.mark.django_db
def test_auth_user_cant_edit_recipe_of_another_user(
    api_not_author_client, recipe_data_update, recipes_detail_url, recipe
):

    response = api_not_author_client.patch(
        recipes_detail_url, recipe_data_update, format='json'
    )
    assert response.status_code == HTTPStatus.FORBIDDEN

    recipe_from_db = Recipe.objects.get(pk=recipe.pk)
    assert_recipe_unchanged(recipe_from_db, recipe)


@pytest.mark.django_db
def test_anonymous_user_cant_delete_recipe(
    api_client, recipes_detail_url, recipe
):
    response = api_client.delete(recipes_detail_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED

    assert Recipe.objects.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
def test_author_can_delete_recipe(api_auth_client, recipes_detail_url, recipe):
    response = api_auth_client.delete(recipes_detail_url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not Recipe.objects.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
def test_auth_user_cant_delete_recipe_of_another_user(
    api_not_author_client, recipes_detail_url, recipe
):
    response = api_not_author_client.delete(recipes_detail_url)
    assert response.status_code == HTTPStatus.FORBIDDEN

    assert Recipe.objects.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'field', ('name', 'text', 'cooking_time', 'image', 'tags', 'ingredients')
)
def test_create_recipe_requires_all_fields(
    api_auth_client, recipes_url, recipe_data, field
):
    recipe_data.pop(field)

    response = api_auth_client.post(recipes_url, recipe_data, format='json')

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert field in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    'field', ('name', 'text', 'cooking_time', 'tags', 'ingredients')
)
def test_update_recipe_requires_required_fields(
    api_auth_client, recipes_detail_url, recipe_data_update, field
):
    recipe_data_update.pop(field)

    response = api_auth_client.patch(
        recipes_detail_url, recipe_data_update, format='json'
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert field in response.data


@pytest.mark.django_db
def test_recipe_tags_filter(api_auth_client, recipes_url, recipes_for_filters):
    response = api_auth_client.get(
        recipes_url, [('tags', 'breakfast'), ('tags', 'lunch')]
    )
    assert response.status_code == HTTPStatus.OK

    assert_recipe_ids(response.data, recipes_for_filters)


@pytest.mark.django_db
def test_create_recipe_rejects_duplicate_tags(
    api_auth_client, recipes_url, recipe_data, tags
):
    recipe_data['tags'] = [tags[0].id, tags[0].id]

    response = api_auth_client.post(recipes_url, recipe_data, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert 'tags' in response.data


@pytest.mark.django_db
def test_create_recipe_rejects_duplicate_ingredients(
    api_auth_client, recipes_url, recipe_data, ingredients
):
    recipe_data['ingredients'] = [
        {'id': ingredients[0].id, 'amount': 10},
        {'id': ingredients[0].id, 'amount': 10},
    ]

    response = api_auth_client.post(recipes_url, recipe_data, format='json')
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert 'ingredients' in response.data


@pytest.mark.django_db
def test_recipe_is_favorited_filter(
    api_auth_client, recipes_url, recipes_for_filters
):
    response = api_auth_client.get(recipes_url, {'is_favorited': 1})
    assert response.status_code == HTTPStatus.OK

    assert_recipe_ids(response.data, recipes_for_filters)


@pytest.mark.django_db
def test_recipe_is_in_shopping_cart_filter(
    api_auth_client, recipes_url, recipes_for_filters
):
    response = api_auth_client.get(recipes_url, {'is_in_shopping_cart': 1})
    assert response.status_code == HTTPStatus.OK

    assert_recipe_ids(response.data, recipes_for_filters)


@pytest.mark.django_db
def test_recipe_author_filter(
    api_auth_client, recipes_url, recipes_for_filters, user
):
    response = api_auth_client.get(recipes_url, {'author': user.id})
    assert response.status_code == HTTPStatus.OK

    assert_recipe_ids(response.data, recipes_for_filters)


@pytest.mark.django_db
def test_recipe_limit_pagination(
    api_auth_client, recipes_url, recipes_for_pagination, user
):
    response = api_auth_client.get(recipes_url, {'limit': 2})
    assert response.status_code == HTTPStatus.OK

    assert len(response.data['results']) == 2
    assert response.data['count'] == len(recipes_for_pagination)


@pytest.mark.django_db
def test_recipe_page_pagination(
    api_auth_client, recipes_url, recipes_for_pagination, user
):
    response = api_auth_client.get(recipes_url, {'limit': 2, 'page': 2})
    assert response.status_code == HTTPStatus.OK

    assert len(response.data['results']) == 2
    assert_recipe_ids(response.data, recipes_for_pagination)


@pytest.mark.django_db
def test_add_recipe_to_favorites_requires_authentication(
    api_client, recipes_favorite_url
):
    response = api_client.post(recipes_favorite_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_delete_recipe_from_favorites_requires_authentication(
    api_client, recipes_favorite_url
):
    response = api_client.delete(recipes_favorite_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_add_recipe_to_favorites(
    api_auth_client, recipes_favorite_url, user, recipe
):
    response = api_auth_client.post(recipes_favorite_url)
    assert response.status_code == HTTPStatus.CREATED

    assert user.favorite_recipes.get(pk=recipe.pk) == recipe


@pytest.mark.django_db
def test_auth_user_cant_add_recipe_to_favorites_twice(
    api_auth_client, recipes_favorite_url, user, recipe
):
    user.favorite_recipes.add(recipe)

    response = api_auth_client.post(recipes_favorite_url)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert user.favorite_recipes.filter(pk=recipe.pk).count() == 1


@pytest.mark.django_db
def test_auth_user_can_delete_recipe_from_favorites(
    api_auth_client, recipes_favorite_url, user, recipe
):
    user.favorite_recipes.add(recipe)

    response = api_auth_client.delete(recipes_favorite_url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not user.favorite_recipes.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
def test_auth_user_cant_delete_recipe_that_is_not_in_favorites(
    api_auth_client, recipes_favorite_url, user, recipe
):
    response = api_auth_client.delete(recipes_favorite_url)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert not user.favorite_recipes.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
def test_add_recipe_to_shopping_cart_requires_authentication(
    api_client, recipes_shopping_cart_url
):
    response = api_client.post(recipes_shopping_cart_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_delete_recipe_from_shopping_cart_requires_authentication(
    api_client, recipes_shopping_cart_url
):
    response = api_client.delete(recipes_shopping_cart_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_add_recipe_to_shopping_cart(
    api_auth_client, recipes_shopping_cart_url, user, recipe
):
    response = api_auth_client.post(recipes_shopping_cart_url)
    assert response.status_code == HTTPStatus.CREATED

    assert user.shopping_cart.get(pk=recipe.pk) == recipe


@pytest.mark.django_db
def test_auth_user_cant_add_recipe_to_shopping_cart_twice(
    api_auth_client, recipes_shopping_cart_url, user, recipe
):
    user.shopping_cart.add(recipe)

    response = api_auth_client.post(recipes_shopping_cart_url)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert user.shopping_cart.filter(pk=recipe.pk).count() == 1


@pytest.mark.django_db
def test_auth_user_can_delete_recipe_from_shopping_cart(
    api_auth_client, recipes_shopping_cart_url, user, recipe
):
    user.shopping_cart.add(recipe)

    response = api_auth_client.delete(recipes_shopping_cart_url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not user.shopping_cart.filter(pk=recipe.pk).exists()


@pytest.mark.django_db
def test_auth_user_cant_delete_recipe_that_is_not_in_shopping_cart(
    api_auth_client, recipes_shopping_cart_url, user, recipe
):
    response = api_auth_client.delete(recipes_shopping_cart_url)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert not user.shopping_cart.filter(pk=recipe.pk).exists()
