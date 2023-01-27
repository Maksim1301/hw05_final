from django.test import TestCase
from ..models import User, LEN_POST, Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='T' * 2 * LEN_POST,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        values = {
            str(self.group): self.group.title,
            str(self.post): self.post.text[:LEN_POST]}
        for value, text in values.items():
            with self.subTest(value=value):
                self.assertEqual(value, text)
