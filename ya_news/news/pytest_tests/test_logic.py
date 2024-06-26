from http import HTTPStatus

import pytest

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_user_cant_use_bad_words(author_client, id_news_for_args):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=id_news_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comment_count = Comment.objects.count()
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == comment_count


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            create_comment_test,
                                            id_news_for_args):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=id_news_for_args)
    comment_count = Comment.objects.count()
    client.post(url, data=create_comment_test)
    assert Comment.objects.count() == comment_count


def test_user_can_create_comment(author_client,
                                 author,
                                 create_comment_test,
                                 id_news_for_args, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=id_news_for_args)
    comment_count = Comment.objects.count()
    response = author_client.post(url, data=create_comment_test)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == comment_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == create_comment_test['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_author_can_edit_comment(author_client,
                                 id_news_for_args,
                                 id_for_args,
                                 comment,
                                 create_comment_test):
    """Авторизованный пользователь может редактироватьсвои комментарии."""
    url = reverse('news:edit', args=id_for_args)
    response = author_client.post(url, data=create_comment_test)
    news_url = reverse('news:detail', args=id_news_for_args)
    assertRedirects(response, f'{news_url}#comments')
    comment.refresh_from_db()
    assert comment.text == create_comment_test['text']


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                comment,
                                                create_comment_test,
                                                id_for_args):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=id_for_args)
    response = not_author_client.post(url, data=create_comment_test)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != create_comment_test['text']


def test_author_can_delete_comment(author_client,
                                   id_for_args,
                                   id_news_for_args):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=id_for_args)
    comment_count = Comment.objects.count()
    response = author_client.post(url)
    news_url = reverse('news:detail', args=id_news_for_args)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == comment_count - 1


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  id_for_args):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=id_for_args)
    comment_count = Comment.objects.count()
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count
