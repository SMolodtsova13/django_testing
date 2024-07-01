from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


SLUG = 'note-slug'
HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SINGUP_URL = reverse('users:signup')
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            author=cls.author,
            text='Текст заметки',
            slug=SLUG
        )
        cls.all_urls = (SINGUP_URL, LOGIN_URL, SUCCESS_URL, HOME_URL,
                        DETAIL_URL, LIST_URL, ADD_URL,
                        EDIT_URL, DELETE_URL, LOGOUT_URL)

    def test_pages_availability_new(self):
        """Все страницы доступны автору."""
        for url in self.all_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_no_author_availability_new(self):
        """Не автору доступны все страницы кроме delete, detail, edit."""
        for url in self.all_urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                inaccessible_pages_not_author = (DETAIL_URL,
                                                 EDIT_URL,
                                                 DELETE_URL)
                if url in inaccessible_pages_not_author:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        """Проверка доступа для анонимного пользователя."""
        for url in self.all_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                inaccessible_pages_anon_users = (LIST_URL, ADD_URL,
                                                 SUCCESS_URL, DETAIL_URL,
                                                 EDIT_URL, DELETE_URL)
                if url in inaccessible_pages_anon_users:
                    redirect_url = f'{LOGIN_URL}?next={url}'
                    self.assertRedirects(response, redirect_url)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)
