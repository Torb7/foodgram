from http import HTTPStatus

from django.urls import reverse
import pytest


@pytest.mark.django_db
def test_registration_with_valid_data(
    api_client, signup_url, user_data, django_user_model
):
    response = api_client.post(signup_url, data=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert django_user_model.objects.filter(email=user_data['email']).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'field', ('email', 'username', 'first_name', 'last_name', 'password')
)
def test_registration_requires_all_fields(
    api_client, signup_url, user_data, field
):
    user_data.pop(field)

    response = api_client.post(signup_url, data=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert field in response.data


@pytest.mark.django_db
@pytest.mark.parametrize('field', ('email', 'username'))
def test_registration_with_duplicate_field(
    api_client, signup_url, user_data, field, user
):
    user_data[field] = getattr(user, field)

    response = api_client.post(signup_url, data=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert field in response.data


@pytest.mark.django_db
def test_login_with_valid_data(api_client, login_url, user, user_password):
    data = {'email': user.email, 'password': user_password}

    response = api_client.post(login_url, data=data)

    assert response.status_code == HTTPStatus.OK

    token = response.data['auth_token']
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    protected_url = reverse('users-me')
    response = api_client.get(protected_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_login_with_wrong_password(api_client, login_url, user):
    data = {'email': user.email, 'password': 'wrong_password'}

    response = api_client.post(login_url, data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_login_with_nonexistent_user(api_client, login_url):
    data = {'email': 'unknown@mail.com', 'password': 'unknown_password'}

    response = api_client.post(login_url, data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
def test_logout_invalidates_auth_token(api_auth_client, logout_url):
    protected_url = reverse('users-me')
    response = api_auth_client.get(protected_url)
    assert response.status_code == HTTPStatus.OK

    response = api_auth_client.post(logout_url)
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = api_auth_client.get(protected_url)
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
def test_successful_password_change(
    api_auth_client, api_client, user, user_password, login_url
):
    new_password = user_password + 'new_password'
    response = api_auth_client.post(
        reverse('users-set-password'),
        {'current_password': user_password, 'new_password': new_password},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = api_client.post(
        login_url, {'email': user.email, 'password': user_password}
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = api_client.post(
        login_url, {'email': user.email, 'password': new_password}
    )
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_wrong_current_password_change(api_auth_client, user, user_password):
    response = api_auth_client.post(
        reverse('users-set-password'),
        {
            'current_password': user_password + 'wrong_current',
            'new_password': user_password + 'new_password',
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
