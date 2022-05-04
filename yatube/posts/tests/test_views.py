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
        # cls.author = User.objects.create_user(username='zhenya',
        #                                       email='zhenyayaya121996@gmail.com',
        #                                       password='1111')
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
                reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': f'{self.post.author}'}),
            'posts/post_detail.html':
                reverse('posts:post_detail', kwargs={'post_id': f'{self.post.id}'}),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse):
                response = self.authorized_client.get(reverse)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
    # """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            # 'pub_date': forms.fields.CharField,
            'author': forms.fields.SlugField,
            'group': forms.fields.ImageField,
        }
    # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """проверка index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, 'zhenya')
        self.assertEqual(first_object.text, 'Текст поста')


    def test_task_detail_pages_show_correct_context(self):
    # """Проверка group_list на правильность контекста."""
        response = (self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 'test-slug'})))
        self.assertEqual(response.context.get('Group').title, 'Тестовая группа')
        self.assertEqual(response.context.get('Group').slug, 'test_slag')
        self.assertEqual(response.context.get('Group').description, 'Тестовое описание')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='zhenya',)
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

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах."""
        posts_on_first_page = 10
        posts_on_second_page = 3
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': f'{self.user.username}'}),
        ]
        for reverse_name in url_pages:
            with self.subTest(reverse_nname=reverse_name):
                response = self.client.get(reverse('reverse_name'))
                self.assertEqual(len(response.context['page_obj']), posts_on_first_page)
                # self.assertEqual(len(self.authorized_client.get(
                #     reverse_).context.get('page_obj')),
                #     posts_on_first_page
                # )
                response = self.client.get(reverse('url') + '?page=2')
                self.assertEqual(len(response.context['page_obj']), posts_on_second_page)
                # self.assertEqual(len(self.authorized_client.get(
                #     reverse_ + '?page=2').context.get('page_obj')),
                #     posts_on_second_page
                # )
