from http import HTTPStatus
from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_not_exist_page(self):
        """Проверка не существующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_exist_page_author(self):
        """Страницы доступны авторизованному пользователю."""
        urls = ['/create/',
                f'/posts/{self.post.id}/edit/']
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        urls_names = ('/',
                      f'/group/{self.group.slug}/',
                      f'/profile/{self.user.username}/',
                      f'/posts/{self.post.id}/')
        for name in urls_names:
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'}
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_404(self):
        """Проверка на отдачу шаблона 404."""
        response = self.authorized_client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
