from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post
# from yatube.yatube.settings import MAX_PAGE_AMOUNT


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
                reverse('posts:group_list',
                        kwargs={'slug': f'{self.group.slug}'}
                        ),
            'posts/profile.html':
                reverse('posts:profile',
                        kwargs={'username': f'{self.post.author}'}
                        ),
            # 'posts/post_detail.html':
            #     reverse('posts:post_detail',
            #             kwargs={'post_id': f'{self.post.id}'}
            #             ),
            'posts/create_post.html': reverse('posts:post_create'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """проверка index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.group, self.post.group)

    def test_group_list_pages_show_correct_context(self):
        """Проверка group_list на правильность контекста."""
        response = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
                    )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.title, self.group.title)
        self.assertEqual(first_object.group.slug, self.group.slug)
        self.assertEqual(first_object.group.description, self.group.description)

    def test_profile_page_show_correct_context(self):
        """Проверка profile на правильность контекста."""
        response = (self.authorized_client.get(

            reverse('posts:profile',

                    kwargs={'username': f'{self.post.author}'}))

        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.group, self.post.group)

    def test_post_detail_page_show_correct_context(self):
        """Проверка post_detail на правильность контекста /<username>/<post_id>/edit/"""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'username': f'{self.user.username}', 'post_id':  f'{self.post.id}'}))
        )
        # self.assertEqual(response.context['author'], self.user)
        # self.assertEqual(response.context.get('post').author.username,
        #                  f'{self.post.author}')
        # self.assertEqual(response.context.get('post').text, 'Текст поста')
        # self.assertEqual(response.context.get('post').group.title,
        #                  f'{self.group}')

    # def test_post_detail_page_show_correct_context(self):
    #     """Проверка create_post на правильность контекста"""
    #     response = self.authorized_client.get(reverse('posts:post_create',))
    #     form_fields = {
    #                'group': forms.fields.CharField,
    #                'text': forms.fields.CharField,
    #            }
    #     for value, expected in form_fields.items():
    #         with self.subTest(value=value):
    #             form_fields = response.context['form'].fields[value]
    #             self.assertIsInstance(form_fields, expected)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()

    def test_first_page_contains_ten_records(self):

        POST_ON_FIRST_PAGE = settings.MAX_PAGE_AMOUNT
        POST_ON_ALL_PAGE = 13 - POST_ON_FIRST_PAGE

        """Проверка: количество постов на первой странице равно 10."""
        response = self.authorized_client.get(reverse('posts:index'))
        list_test = response.context['page_obj']
        self.assertEqual(len(list_test), POST_ON_FIRST_PAGE)

        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        list_test = response.context['page_obj']
        self.assertEqual(len(list_test), POST_ON_ALL_PAGE)

    # def test_paginator_pages(self):
    #     """проверка пагинации на страницах"""
    #     list_pages = [
    #         reverse('posts:index'),
    #         reverse('posts:group_list', kwargs={'slug': self.group.slug}),
    #         reverse('posts:profile', kwargs={'username': self.user.username}),
    #     ]
    #
    #     for lists in list_pages:
    #         with self.subTest():
    #             response = self.authorized_client.get(lists)
    #             self.assertEqual(response.context.get('page_obj'))


