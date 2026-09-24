from http import HTTPStatus

from django.urls import reverse
import pytest

from .helpers import assert_user_response_data


@pytest.mark.django_db
def test_anonymous_user_can_get_users(api_client, user, users_url):
    response = api_client.get(users_url)
    assert response.status_code == HTTPStatus.OK

    assert response.data['count'] == 1
    assert_user_response_data(response.data['results'][0], user, False)


@pytest.mark.django_db
def test_anonymous_user_can_get_users_detail(
    api_client, user, users_detail_url
):
    response = api_client.get(users_detail_url)
    assert response.status_code == HTTPStatus.OK

    assert_user_response_data(response.data, user, False)


def test_anonymous_user_cant_get_the_current_user_data(
    api_client, users_me_url
):
    response = api_client.get(users_me_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_get_the_current_user_data(
    api_auth_client, user, users_me_url
):
    response = api_auth_client.get(users_me_url)
    assert response.status_code == HTTPStatus.OK

    assert_user_response_data(response.data, user, False)


def test_anonymous_user_cant_add_avatar(api_client, avatar_url):
    response = api_client.put(avatar_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_add_avatar(
    api_auth_client, user, avatar_url, avatar_image
):
    response = api_auth_client.put(avatar_url, {'avatar': avatar_image})
    assert response.status_code == HTTPStatus.OK

    assert response.data['avatar']
    user.refresh_from_db()
    assert user.avatar


def test_anonymous_user_cant_delete_avatar(api_client, avatar_url):
    response = api_client.delete(avatar_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_delete_avatar(
    api_auth_client, user, avatar_url, avatar_image
):
    response = api_auth_client.put(avatar_url, {'avatar': avatar_image})
    user.refresh_from_db()
    assert user.avatar

    response = api_auth_client.delete(avatar_url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    user.refresh_from_db()
    assert not user.avatar


def test_anonymous_user_cant_get_subscriptions(api_client, subscriptions_url):
    response = api_client.get(subscriptions_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_get_subscriptions(
    api_auth_client, subscriptions_url, subscribed_user, another_user
):
    response = api_auth_client.get(subscriptions_url)
    assert response.status_code == HTTPStatus.OK

    assert response.data['count'] == 1
    assert_user_response_data(response.data['results'][0], another_user, True)


@pytest.mark.django_db
def test_anonymous_user_cant_subscribe_to_user(api_client, subscribe_url):
    response = api_client.post(subscribe_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_subscribe_to_user(
    api_auth_client, subscribe_url, user, another_user
):
    response = api_auth_client.post(subscribe_url)
    assert response.status_code == HTTPStatus.CREATED

    assert user.following.filter(pk=another_user.pk).exists()
    assert_user_response_data(response.data, another_user, True)


@pytest.mark.django_db
def test_anonymous_user_cant_unsubscribe_from_user(api_client, subscribe_url):
    response = api_client.delete(subscribe_url)

    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_can_unsubscribe_from_user(
    api_auth_client, subscribe_url, subscribed_user, another_user
):
    response = api_auth_client.delete(subscribe_url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    assert not subscribed_user.following.filter(pk=another_user.pk).exists()


@pytest.mark.django_db
def test_auth_user_cant_duplicate_subscription(
    api_auth_client, subscribe_url, subscribed_user, another_user
):
    response = api_auth_client.post(subscribe_url)
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert subscribed_user.following.filter(pk=another_user.pk).count() == 1


@pytest.mark.django_db
def test_auth_user_cant_subscribe_to_themselves(api_auth_client, user):
    response = api_auth_client.post(
        reverse('users-subscribe', args=(user.pk,))
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert not user.following.filter(pk=user.pk).exists()


@pytest.mark.django_db
def test_auth_user_cant_unsubscribe_from_non_existent_subscription(
    api_auth_client, user, another_user
):
    response = api_auth_client.delete(
        reverse('users-subscribe', args=(another_user.pk,))
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    assert not user.following.filter(pk=another_user.pk).exists()
