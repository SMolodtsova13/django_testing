from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, expected_status',
    ((pytest.lazy_fixture('home_url')),
     (pytest.lazy_fixture('users_login_url')),
     (pytest.lazy_fixture('users_logout_url')),
     (pytest.lazy_fixture('users_singnup_url')),
     (pytest.lazy_fixture('users_logout_url'),)
     )
)
def test_pages_availability_for_anonymous_user(client,name,):
    """
    Главная страница, регистрация, входа, выхода, доступны пользователям.
    Страница отдельной новости доступна анонимному пользователю.
    """
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    ((pytest.lazy_fixture('author_client'), HTTPStatus.OK),
     (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),),
)
@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('news_delete_url'),
     pytest.lazy_fixture('news_edit_url')),
)
def test_pages_availability_for_different_users(parametrized_client,
                                                name,
                                                expected_status):
    """
    Страницы удаления и редактирования доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы
    редактирования или удаления чужих комментариев (ошибка 404).
    """
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('news_delete_url'),
     pytest.lazy_fixture('news_edit_url')),
)
def test_redirect_for_anonymous_client(client, name, users_login_url):
    """Анонимный пользователь перенаправляется на страницу авторизации."""
    expected_url = f'{users_login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
