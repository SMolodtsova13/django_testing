import pytest

from datetime import datetime, timedelta

from django.test.client import Client
from django.conf import settings

from news.models import News, Comment


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
