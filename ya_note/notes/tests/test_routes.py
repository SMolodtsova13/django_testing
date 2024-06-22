from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.notes = Note.objects.create(
            author=cls.author,
            text='Текст заметки'
        )
    """Главная страница доступна анонимному пользователю.
    Страницы регистрации пользователей,
    входа в учётную запись и выхода из неё доступны всем пользователям."""
    def test_pages_availability(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    """Аутентифицированному пользователю доступна страница
    со списком заметок notes/,страница успешного добавления заметки done/,
    страница добавления новой заметки add/."""
    def test_pages_availability_for_auth_user(self):
        urls = (
            ('notes:list'),
            ('notes:add'),
            ('notes:success'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                self.client.force_login(self.reader)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    """Страницы отдельной заметки, удаления и редактирования заметки
    доступны только автору заметки.
    Если на эти страницы попытается зайти другой пользователь —
    вернётся ошибка 404."""
    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail',):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    """При попытке перейти на страницу списка заметок,
    страницу успешного добавления записи,
    страницу добавления заметки, отдельной заметки,
    редактирования или удаления заметки анонимный пользователь
    перенаправляется на страницу логина."""
    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:detail', (self.notes.slug,)),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args,)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
