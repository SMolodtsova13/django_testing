import pytest

from django.test.client import Client

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
def id_for_args(comment):
    return (comment.id,)


@pytest.fixture
def comment_test():
    return {
        'text': 'Новый текст комментария',
        'id': '2',
    }



# @pytest.fixture
# def bad_comment_test():
#     return {
#         'text': 'Новый текст комментария - редиска',
#         'id': '3',
#     }


# @pytest.fixture
# def comment_test(author, news):
#     comment_test = Comment.objects.create(
#         news=news,
#         text='Текст комментария',
#         author=author,
#         id=2,
#     )
#     return comment_test
