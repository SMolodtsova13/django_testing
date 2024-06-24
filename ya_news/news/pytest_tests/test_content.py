import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING, CommentForm


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, id_news_for_args):
    """Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости"""
    url = reverse('news:detail', args=id_news_for_args)
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, id_news_for_args):
    """Авторизованному пользователю доступна форма для отправки комментария
    на странице отдельной новости"""
    url = reverse('news:detail', args=id_news_for_args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)



"""Количество новостей на главной странице — не более 10."""
"""Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка."""
"""Комментарии на странице отдельной новости отсортированы в хронологическом порядке:
старые в начале списка, новые — в конце."""
