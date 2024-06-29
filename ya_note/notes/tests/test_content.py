from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestPagesNote(TestCase):
    ADD_URL = 'notes:add'
    EDIT_URL = 'notes:edit'
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст заметки',
                                       slug='slug',
                                       author=cls.author,
                                       )
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.add_url = reverse(cls.ADD_URL, args=None)
        cls.edit_url = reverse(cls.EDIT_URL, args=(cls.note.slug,))

    def test_note_in_list_for_author(self):
        """Заметка передаётся на страницу со списком заметок."""
        response = self.author_client.get(self.LIST_URL)
        response.context['object_list']
        self.assertEqual(Note.objects.count(), 1)
        notes = Note.objects.get()
        self.assertEqual(notes.text, self.note.text)
        self.assertEqual(notes.author, self.note.author)
        self.assertEqual(notes.title, self.note.title)
        self.assertEqual(notes.slug, self.note.slug)

    def test_note_not_in_list_for_another_user(self):
        """В список заметок одного пользователя не попадают заметки другого."""
        response = self.auth_client.get(self.LIST_URL)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 0)
        self.assertEqual(object_list.first(), None)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
