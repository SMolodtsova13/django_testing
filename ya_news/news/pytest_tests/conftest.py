from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def news_detail_url(id_news_for_args):
    return reverse('news:detail', args=id_news_for_args)


@pytest.fixture
def users_login_url():
    return reverse('users:login')


@pytest.fixture
def users_logout_url():
    return reverse('users:logout')


@pytest.fixture
def users_singnup_url():
    return reverse('users:signup')


@pytest.fixture
def news_edit_url(id_for_args):
    return reverse('news:edit', args=id_for_args)


@pytest.fixture
def news_delete_url(id_for_args):
    return reverse('news:delete', args=id_for_args)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def create_news_test():
    today = datetime.today()
    all_news = [News(title=f'Новость {index}',
                     text='Просто текст.',
                     date=today - timedelta(days=index)
                     )
                for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
                ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def id_news_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def create_new_comment():
    today = datetime.today()
    all_comment = [Comment(text=f'Комментарий {index}',
                           date=today - timedelta(days=index),
                           )
                   for index in range(settings.NEWS_COUNT_ON_HOME_PAGE)
                   ]
    return Comment.objects.bulk_create(all_comment)


@pytest.fixture
def id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def create_comment_test():
    return {
        'text': 'Новый текст комментария',
    }
