from django.urls import reverse

SLUG = 'note-slug'
HOME_URL = reverse('notes:home',)
LIST_URL = reverse('notes:list',)
ADD_URL = reverse('notes:add',)
SUCCESS_URL = reverse('notes:success',)
LOGIN_URL = reverse('users:login',)
LOGOUT_URL = reverse('users:logout',)
SINGUP_URL = reverse('users:signup',)
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
