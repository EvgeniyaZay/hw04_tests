from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slag',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Текст поста',
            # pub_date='3 мая 2022',
            author=cls.user,
            group=cls.group,

        )

    def setUp(self):
        # self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html':
                reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}
                        ),
            'posts/profile.html':
                reverse('posts:profile', kwargs={'username': f'{self.post.author}'}
                        ),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
                        ),
            'posts/create_post.html': reverse('posts:post_create'),
            # 'posts/create_post.html': reverse('posts:edit', kwargs={'post_id': self.post.id, }),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """проверка index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Текст поста')

    def test_group_list_pages_show_correct_context(self):
        """Проверка group_list на правильность контекста."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        )
        self.assertEqual(response.context['group'], self.group)

    def test_profile_page_show_correct_context(self):
        """Проверка group_list на правильность контекста."""
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': f'{self.user.username}'}))
        )
        self.assertEqual(response.context['author'], self.user)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(13):
            Post.objects.create(
                text=f'Пост #{i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.authorized_client = Client()

        """Проверка пагинации на страницах."""

    def test_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test_slug'})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
