from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from slugify import slugify
# from pytils.translit import slugify

from models import Note
from forms import WARNING

User = get_user_model()


class TestNotesCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    """Анонимный пользователь не может создать заметку."""
    def test_anonymous_user_cant_create_notes(self):
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    """Залогиненный пользователь может создать заметку."""
    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    """Невозможно создать две заметки с одинаковым slug."""
    def test_user_cant_create_same_notes(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        bad_words_data = {'text': 'Какой-то текст',
                          'slug': 'new-slug'}
        self.form_data['slug'] = bad_words_data['slug']
        response = self.auth_client.post(self.url, data=bad_words_data)
        self.assertFormError(response,
                             form='form',
                             field='slug',
                             errors=(f'{bad_words_data["slug"]}{WARNING}'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    """Если при создании заметки не заполнен slug, то он
    формируется автоматически, с помощью функции pytils.translit.slugify."""
    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes = Note.objects.create(title='Заголовок',
                                        text=cls.NOTE_TEXT,
                                        slug='slug',
                                        author=cls.author,
                                        )
        cls.notes_url = reverse('notes:detail', args=(cls.notes.slug,))
        cls.url = reverse('notes:success')
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'new-slug'
        }

    """Пользователь удалять свои заметки"""
    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    """Пользователь не может удалять чужие заметки."""
    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    """Пользователь может редактировать свои заметки"""
    def test_author_can_edit_notes(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.slug, self.form_data['slug'])

    """Пользователь не может редактировать чужие заметки"""
    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NOTE_TEXT)
