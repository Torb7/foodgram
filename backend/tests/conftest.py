import pytest
from rest_framework.test import APIClient
from django.urls import reverse


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
def login_url():
    return reverse('login')


@pytest.fixture
def logout_url():
    return reverse('logout')


@pytest.fixture
def signup_url():
    return reverse('users-list')
