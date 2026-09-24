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
