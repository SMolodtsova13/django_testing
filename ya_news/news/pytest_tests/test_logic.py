import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_cant_use_bad_words(author_client, id_news_for_args):
    """Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку."""
    url = reverse('news:detail', args=id_news_for_args)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client,
                                            comment_test,
                                            id_news_for_args):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=id_news_for_args)
    client.post(url, data=comment_test)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client,
                                 author,
                                 comment_test,
                                 id_news_for_args, news):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=id_news_for_args)
    response = author_client.post(url, data=comment_test)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_test['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_author_can_edit_comment(author_client,
                                 id_news_for_args,
                                 id_for_args,
                                 comment,
                                 comment_test):
    """Авторизованный пользователь может редактироватьсвои комментарии."""
    url = reverse('news:edit', args=id_for_args)
    response = author_client.post(url, data=comment_test)
    news_url = reverse('news:detail', args=id_news_for_args)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_test['text']


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                comment,
                                                comment_test,
                                                id_for_args):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=id_for_args)
    response = not_author_client.post(url, data=comment_test)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != comment_test['text']


def test_author_can_delete_comment(author_client,
                                   id_for_args,
                                   id_news_for_args):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', args=id_for_args)
    response = author_client.post(url, )
    news_url = reverse('news:detail', args=id_news_for_args)
    url_to_comments = news_url + '#comments'
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  id_for_args):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', args=id_for_args)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
