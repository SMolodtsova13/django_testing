import pytest

from django.test.client import Client

from yanews import settings

from news.models import News, Comment

from datetime import datetime, timedelta


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
        id=1,
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
        id=1,
    )
    return comment


@pytest.fixture
def new_comment(author, news):
    new_comment = Comment.objects.create(
        news=news,
        date=datetime.today(),
        text='Текст комментария',
        author=author,
        id=2,
    )
    return new_comment


@pytest.fixture
def new_comment_test(author, news):
    new_comment_test = Comment.objects.create(
        news=news,
        date=datetime.today() - timedelta(days=1),
        text='Текст комментария',
        author=author,
        id=3,
    )
    return new_comment_test


@pytest.fixture
def id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def comment_test():
    return {
        'text': 'Новый текст комментария',
        'id': '4',
    }
