import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Comment, User
from ..forms import PostForm

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_auth')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group')

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.posts_count = Post.objects.count()

    def test_create_guest_client(self):
        """Тестирование создания поста неавторизованного
        пользователя."""
        form_data = {'text': 'Тестовый текст'}
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(),
                         self.posts_count,
                         'Поcт добавлен в базу')

    def test_create_post(self):
        """Тестирование создания поста и
        добавление фото."""
        Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        new_posts = Post.objects.latest('id')
        values = {
            form_data['text']: new_posts.text,
            self.group.id: new_posts.group.id,
            self.user: new_posts.author}
        for value, new_post in values.items():
            with self.subTest(value=value):
                self.assertEqual(value, new_post)
        self.assertEqual(Post.objects.count(),
                         self.posts_count + 1,
                         'Поcт не добавлен в базу')
        self.assertFalse(new_posts.image is None)

    def test_edit_post(self):
        """Тестирование редактирование поста."""
        form_data = {'text': 'Тестовый текст',
                     'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        edit_posts = Post.objects.get(id=self.post.id)
        values = {
            form_data['text']: edit_posts.text,
            self.group.id: edit_posts.group.id,
            self.user: edit_posts.author}
        for value, edit_post in values.items():
            with self.subTest(value=value):
                self.assertEqual(value, edit_post)
        self.assertEqual(Post.objects.count(),
                         self.posts_count,
                         'Поcт добавлен в базу')

    def test_add_comment(self):
        """Тестирование добавление комментариев."""
        form_data = {'text': 'Текст комментария'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        comment_count = Comment.objects.count()
        new_comment = Comment.objects.get(id=self.post.id)
        self.assertContains(response, 'Текст комментария')
        self.assertEqual(form_data['text'], new_comment.text)
        self.assertEqual(Comment.objects.count(), comment_count)
