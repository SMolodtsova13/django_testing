import pytest
from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Главная страница, cтраницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны анонимным пользователям."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_page(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status, comment,
):
    """Страницы удаления и редактирования доступны автору комментария.
    Авторизованный пользователь не может зайти на страницы
    редактирования или удаления чужих комментариев (ошибка 404)."""
    url = reverse(name,  args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    ),
)
def test_redirect_for_anonymous_client(client, name, args):
    """При попытке перейти на страницу редактирования или удалени комментария
    анонимный пользователь перенаправляется на страницу авторизации."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
