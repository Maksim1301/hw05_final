class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД,
        # она понадобится для тестирования страницы deals:task_detail
        Task.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_about_page_uses_correct_template(self):
        """URL-адрес использует шаблон deals/added.html."""
        response = self.authorized_client.get(reverse('deals:task_added'))
        self.assertTemplateUsed(response, 'deals/added.html')

    def test_home_page_correct_template(self):
        """URL-адрес использует шаблон deals/home.html."""
        response = self.authorized_client.get(reverse('deals:home'))
        self.assertTemplateUsed(response, 'deals/home.html')

    def test_task_list_page_authorized_uses_correct_template(self):
        """URL-адрес использует шаблон deals/task_list.html."""
        response = self.authorized_client.get(reverse('deals:task_list'))
        self.assertTemplateUsed(response, 'deals/task_list.html')

    def test_task_detail_pages_authorized_uses_correct_template(self):
        """URL-адреса используют шаблон deals/task_detail.html."""
        response = self.authorized_client.\
            get(reverse('deals:task_detail', kwargs={'slug': 'test-slug'}))
        self.assertTemplateUsed(response, 'deals/task_detail.html')