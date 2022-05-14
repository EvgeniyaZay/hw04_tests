from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slag',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='auth')
        # cls.form = PostForm()

    def setUp(self):
        self.guest_user = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_create_post(self):
        """проверка создания записи авторизованным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Текст поста',
                group=self.group.id
            ).exists()
        )
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(self.post.text)
        # self.assertEqual(self.post.author, self.user)
        # self.assertEqual(self.post.group_id, self.group.title)

    def test_authorized_user_post_edit(self):
        """проверка редактирования записи авторизованным клиентом"""
        post = Post.objects.create(
            author=self.user,
            text='Текст поста',
            group=self.group
        )
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post.id}
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # post = Post.objects.latest('id')
        # self.assertEqual(self.post.text, form_data['text'])
        # self.assertEqual(self.post.author, self.user)
        # self.assertEqual(self.post.group_id, form_data['group'])

    def test_guest_user_create_post(self):
        """проверка создания записи неавторизованным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            f'{reverse("users:login")}?next={reverse("posts:post_create")}'
        )
        self.assertEqual(Post.objects.count(), posts_count)

