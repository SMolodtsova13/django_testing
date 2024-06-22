from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from models import Note
from forms import NoteForm

User = get_user_model()


class TestPagesNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.notes = Note.objects.create(title='Заголовок',
                                        text='Текст заметки',
                                        slug='slug',
                                        author=cls.author,
                                        )
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:list')

    """Отдельная заметка передаётся на страницу со списком заметок
    в списке object_list в словаре context."""
    def test_note_in_list_for_author(self):
        response = self.author_client.get(self.url)
        object_list = response.context['object_list']
        self.assertIn(self.notes, object_list)

    """В список заметок одного пользователя не попадают
    заметки другого пользователя."""
    def test_note_not_in_list_for_another_user(self):
        response = self.auth_client.get(self.url)
        object_list = response.context['object_list']
        self.assertNotIn(self.notes, object_list)

    """На страницы создания и редактирования заметки передаются формы."""
    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args,)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
