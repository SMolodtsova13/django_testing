from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_user_cant_use_bad_words(author_client, news_detail_url):
    """Если комментарий содержит запрещённые слова,он не будет опубликован.
    Форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comment_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == comment_count


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            create_comment_test,
                                            news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comment_count = Comment.objects.count()
    client.post(news_detail_url, data=create_comment_test)
    assert Comment.objects.count() == comment_count


def test_user_can_create_comment(author_client,
                                 author,
                                 create_comment_test,
                                 news_detail_url,
                                 news):
    """Авторизованный пользователь может отправить комментарий."""
    comment_count = Comment.objects.count()
    response = author_client.post(news_detail_url, data=create_comment_test)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comment_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == create_comment_test['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_author_can_edit_comment(author_client,
                                 news_detail_url,
                                 news_edit_url,
                                 create_comment_test,
                                 news,
                                 author):
    """Авторизованный пользователь может редактироватьсвои комментарии."""
    coment_count = Comment.objects.count
    response = author_client.post(news_edit_url, data=create_comment_test)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert coment_count == Comment.objects.count
    comment = Comment.objects.get()
    assert comment.text == create_comment_test['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                create_comment_test,
                                                news_edit_url,
                                                not_author,
                                                news):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = not_author_client.post(news_edit_url, data=create_comment_test)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get()
    assert comment.text != create_comment_test['text']
    assert comment.author != not_author
    assert comment.news == news


def test_author_can_delete_comment(author_client,
                                   news_delete_url,
                                   news_detail_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comment_count = Comment.objects.count()
    response = author_client.post(news_delete_url)
    assertRedirects(response, f'{news_detail_url}#comments')
    assert Comment.objects.count() == comment_count - 1


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  news_delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comment_count = Comment.objects.count()
    response = not_author_client.post(news_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comment_count
