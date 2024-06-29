from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()

SLUG = 'note-slug'
ADD_URL = reverse('notes:add',)
SUCCESS_URL = reverse('notes:success',)
LOGIN_URL = reverse('users:login',)
LOGOUT_URL = reverse('users:logout',)


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
        redirect_url = f'{LOGIN_URL}?next={ADD_URL}'
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
        notes_count = Note.objects.count()
        self.auth_client.post(ADD_URL, data=self.form_data_test)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он
        формируется автоматически, с помощью функции pytils.translit.slugify.
        """
        self.form_data.pop('slug')
        self.assertEqual(Note.objects.count(), 0)
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(Note.objects.count(), 1)


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст заметки'
    EDIT_URL = 'notes:edit'
    DELETE_URL = 'notes:delete'

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
        cls.edit_url = reverse(cls.EDIT_URL, args=(cls.notes.slug,))
        cls.delete_url = reverse(cls.DELETE_URL, args=(cls.notes.slug,))
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': cls.NEW_NOTE_TEXT,
            'slug': 'new-slug'
        }

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки"""
        notes_count = Note.objects.count()
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        notes_count = Note.objects.count()
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, Note.objects.count())

    def test_author_can_edit_notes(self):
        """Пользователь может редактировать свои заметки"""
        self.assertEqual(Note.objects.count(), 1)
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.notes.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужие заметки"""
        self.assertEqual(Note.objects.count(), 1)
        notes = Note.objects.get()
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_edit = Note.objects.get()
        self.assertEqual(notes.text, notes_edit.text)
        self.assertEqual(notes.author, notes_edit.author)
        self.assertEqual(notes.title, notes_edit.title)
        self.assertEqual(notes.slug, notes_edit.slug)
