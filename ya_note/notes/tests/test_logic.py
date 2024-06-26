from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from pytils.translit import slugify

from constants import ADD_URL, DELETE_URL, EDIT_URL, LOGIN_URL, SUCCESS_URL

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNotesCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.form_data_test = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'new-slug'
        }

    def test_anonymous_user_cant_create_notes(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        redirect_url = f'{LOGIN_URL}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.auth_client.post(ADD_URL, data=self.form_data)
        response = self.auth_client.post(ADD_URL, data=self.form_data_test)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.form_data_test['slug'] + WARNING)
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он
        формируется автоматически, с помощью функции pytils.translit.slugify.
        """
        self.form_data.pop('slug')
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


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
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'new-slug'
        }

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки"""
        response = self.author_client.delete(DELETE_URL)
        notes_count = Note.objects.count()
        self.assertRedirects(response, SUCCESS_URL)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        notes_count = Note.objects.count()
        response = self.reader_client.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, Note.objects.count())

    def test_author_can_edit_notes(self):
        """Пользователь может редактировать свои заметки"""
        response = self.author_client.post(EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, self.form_data['title'])
        self.assertEqual(self.notes.text, self.form_data['text'])
        self.assertEqual(self.notes.slug, self.form_data['slug'])

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки"""
        response = self.reader_client.post(EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.NOTE_TEXT)
