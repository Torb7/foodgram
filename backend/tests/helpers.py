from urllib.parse import urlparse


def assert_user_response_data(data, user, expected_is_subscribed):
    assert data['id'] == user.id
    assert data['email'] == user.email
    assert data['username'] == user.username
    assert data['first_name'] == user.first_name
    assert data['last_name'] == user.last_name
    assert data['is_subscribed'] is expected_is_subscribed

    if user.avatar:
        assert urlparse(data['avatar']).path == user.avatar.url
    else:
        assert data['avatar'] is None


def assert_recipe_matches_data(data, recipe, user, tags):
    assert recipe.name == data['name']
    assert recipe.text == data['text']
    assert recipe.cooking_time == data['cooking_time']
    assert recipe.author == user

    assert recipe.image
    assert recipe.image.storage.exists(recipe.image.name)

    assert set(recipe.tags.all()) == set(tags)

    actual_ingredients = {
        (obj.ingredient.id, obj.amount)
        for obj in recipe.recipe_ingredients.all()
    }
    expected_ingredients = {
        (ingredient['id'], ingredient['amount'])
        for ingredient in data['ingredients']
    }
    assert expected_ingredients == actual_ingredients


def assert_recipe_response_data(
    data, recipe, expected_is_favorited, expected_is_in_shopping_cart
):
    assert data['id'] == recipe.id
    assert data['name'] == recipe.name
    assert data['text'] == recipe.text
    assert data['cooking_time'] == recipe.cooking_time
    assert urlparse(data['image']).path == recipe.image.url
    assert data['is_favorited'] is expected_is_favorited
    assert data['is_in_shopping_cart'] is expected_is_in_shopping_cart

    assert_user_response_data(data['author'], recipe.author, False)


def assert_recipe_unchanged(actual, expected):
    assert actual.name == expected.name
    assert actual.text == expected.text
    assert actual.cooking_time == expected.cooking_time
    assert actual.author == expected.author
    assert actual.image == expected.image
    assert set(actual.tags.all()) == set(expected.tags.all())
    assert set(actual.recipe_ingredients.all()) == set(
        expected.recipe_ingredients.all()
    )


def assert_recipe_ids(data, recipes_for_filters):
    returned_ids = {recipe['id'] for recipe in data['results']}
    expected_ids = {recipes_for_filters[0].id, recipes_for_filters[1].id}
    assert returned_ids == expected_ids


def assert_ingredient_response_data(data, ingredient):
    assert data['id'] == ingredient.id
    assert data['name'] == ingredient.name
    assert data['measurement_unit'] == ingredient.measurement_unit


def assert_tag_response_data(data, tag):
    assert data['id'] == tag.id
    assert data['name'] == tag.name
    assert data['slug'] == tag.slug
