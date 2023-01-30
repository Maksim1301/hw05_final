from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from ..utils import TEN_PAGES
from ..models import Group, Post, Follow, User

THREE_PAGES = 3


class PostPagesTests(TestCase):
    """Тестирование работы шаблонов"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif')
        cls.user = User.objects.create_user(username='test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_views_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list',
                        kwargs={'slug': f'{self.group.slug}'})),
            'posts/profile.html': (
                reverse('posts:profile',
                        kwargs={'username': f'{self.user.username}'})),
            'posts/post_detail.html': (
                reverse('posts:post_detail',
                        kwargs={'post_id': f'{self.post.id}'})),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/follow.html': reverse('posts:follow_index')
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_context(self):
        """Шаблон index, grout_list, profile
        сформирован с правильным контекстом."""
        response_tuple = (
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(
                reverse('posts:group_list',
                        kwargs={'slug': f'{self.group.slug}'})),
            self.authorized_client.get(
                reverse('posts:profile',
                        kwargs={'username': f'{self.user.username}'})))
        for response in response_tuple:
            self.assertIn('page_obj', response.context)
        for response in response_tuple:
            context_objects = {
                self.user: response.context['page_obj'][0].author,
                self.post.text: response.context['page_obj'][0].text,
                self.group.slug: response.context['page_obj'][0].group.slug,
                self.post.image: response.context['page_obj'][0].image}
            for reverse_name, response_name in context_objects.items():
                with self.subTest(reverse_name=reverse_name):
                    self.assertEqual(response_name, reverse_name)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}))
        self.assertIn('post', response.context)
        post_text = {response.context['post'].text: self.post.text,
                     response.context['post'].group: self.group,
                     response.context['post'].id: self.post.id,
                     response.context['post'].author: self.user.username,
                     response.context['post'].image: self.post.image}
        for value, expected in post_text.items():
            self.assertEqual(post_text[value], expected)

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField}
        self.assertIn('form', response.context)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_added_correctly(self):
        """При создании поста, он будет добавлен."""
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        values = (response_index,
                  response_group,
                  response_profile)
        for value in values:
            with self.subTest(value=value):
                self.assertIn(self.post, value.context['page_obj'])

    def test_post_not_added_group2(self):
        """При создании поста он не попал в другую группу."""
        user2 = User.objects.create_user(username='test_auth2')
        group2 = Group.objects.create(title='Тестовая группа 2',
                                      slug='test_group2')
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост от другого автора',
            author=user2,
            group=group2)
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count,
                         'поста нет в другой группе')
        self.assertNotIn(post, profile,
                         'поста нет в группе другого пользователя')

    def test_cache_index(self):
        """Проверка и очистка кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.content
        Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user)
        response_old = self.authorized_client.get(reverse('posts:index'))
        posts_old = response_old.content
        self.assertEqual(posts_old, posts)
        cache.clear()
        response_new = self.authorized_client.get(reverse('posts:index'))
        posts_new = response_new.content
        self.assertNotEqual(posts_old, posts_new)


class PaginatorViewsTest(TestCase):
    """Тестирование паджинатора."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Basov')

    def setUp(self):
        cache.clear()
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        num_post: list = []
        for i in range(TEN_PAGES + THREE_PAGES):
            num_post.append(Post(text=f'Тестовый текст {i}',
                                 group=self.group,
                                 author=self.user))
        Post.objects.bulk_create(num_post)

        self.page_names = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': 'test_group'}),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
        }

    def test_first_page_contains_ten_records(self):
        """Тестирование паджинатора на первой страницы."""
        for pages in self.page_names:
            with self.subTest(pages=pages):
                response = self.client.get(pages)
                self.assertEqual(len(response.context['page_obj']),
                                 TEN_PAGES)

    def test_second_page_contains_three_records(self):
        """Тестирование паджинатора на второй страницы."""
        for pages in self.page_names:
            with self.subTest(pages=pages):
                response = self.client.get(pages + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 THREE_PAGES)


class FollowViewsTest(TestCase):
    """Тестирование работы подписок"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='Автор поста'
        )
        cls.follower = User.objects.create(
            username='Подписчик'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_create_follow_to_author(self):
        """Проверка подписки на автора."""
        self.assertEqual(Follow.objects.count(), 0)
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    args=(self.author.username,)))
        self.assertEqual(Follow.objects.count(), 1)
        follow_obj = Follow.objects.first()
        self.assertEqual(follow_obj.author, self.author)
        self.assertEqual(follow_obj.user, self.follower)

    def test_delete_follow_to_author(self):
        """Проверка удаления подписки."""
        self.assertEqual(Follow.objects.count(), 0)
        Follow.objects.create(
            author=self.author,
            user=self.follower)
        self.assertEqual(Follow.objects.count(), 1)
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    args=(self.author.username,)))
        self.assertEqual(Follow.objects.count(), 0)
        following = Follow.objects.filter(
            author=self.author,
            user=self.follower).exists()
        self.assertFalse(following)

    def test_new_post_follow_to_author(self):
        """Новая запись будет у тех кто подписан."""
        Post.objects.create(
            author=self.author,
            text='Тестовый текст')
        self.assertEqual(Follow.objects.count(), 0)
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    args=(self.author.username,)))
        self.assertEqual(Follow.objects.count(), 1)
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    args=(self.author,)))
