from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем этого пользователя (Не автор, 'HasNoName')
        self.authorized_client.force_login(self.user)
        # Создаем третий клиент
        self.author_client = Client()
        # Ссылаемся на пользователя (Автор, 'Author')
        self.user_author = PostUrlTests.user
        # Авторизуем пользователя (Автор, 'Author')
        self.author_client.force_login(self.user_author)

    def test_posts_urls_all_for_guest(self):
        """Страницы / доступные неавторизованному пользователю."""
        urls = {
            '/',
            '/group/test_slug/',
            '/profile/HasNoName/',
            '/posts/1/',
        }
        for address in urls:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_create_for_guest(self):
        """Страница create / недоступна для неавторизованного пользователя"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_posts_urls_edit_for_guest(self):
        """Страница edit / недоступна для неавторизованного пользователя"""
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_posts_urls_unexisting_page_for_guest(self):
        """Страницы / с кодом 404 для неавторизованного пользователя"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_urls_all_for_authorized_user(self):
        """Страницы / доступные авторизованному пользователю."""
        urls = {
            '/',
            '/group/test_slug/',
            '/profile/HasNoName/',
            '/posts/1/',
            '/create/'
        }
        for address in urls:
            with self.subTest():
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_create_for_authorized_user(self):
        """Страница edit / недоступна для
        авторизованного пользователя(не автор)"""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_posts_urls_unexisting_page_for_authorized_user(self):
        """Страницы / с кодом 404 для авторизованного пользователя(не автор)"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_urls_all_for_author_user(self):
        """Страницы / доступные автору."""
        urls = {
            '/',
            '/group/test_slug/',
            '/profile/HasNoName/',
            '/posts/1/',
            '/create/'
        }
        for address in urls:
            with self.subTest():
                response = self.author_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_create_for_autho_user(self):
        """Страница edit / доступна для автора"""
        response = self.author_client.get('/posts/1/edit/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_urls_unexisting_page_for_author_user(self):
        """Страницы / с кодом 404 для автора"""
        response = self.author_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_urls_follow_for_guest_user(self):
        """Страница follow / недоступна для Гостя"""
        response = self.guest_client.get(
            f'/profile/{self.user.username}/follow/', follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/profile/{self.user.username}/follow/')

    def test_posts_urls_unfollow_for_guest_user(self):
        """Страница unfollow / недоступна для Гостя"""
        response = self.guest_client.get(
            f'/profile/{self.user.username}/unfollow/', follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/profile/{self.user.username}/unfollow/')

    def test_posts_urls_follow_for_authorized_user(self):
        """Страница follow / доступна для Авторизованного пользователя"""
        response = self.authorized_client.get(
            f'/profile/{self.user.username}/follow/', follow=True)
        self.assertRedirects(
            response,
            f'/profile/{self.user.username}/')

    def test_posts_urls_unfollow_for_authorized_user(self):
        """Страница unfollow / доступна для Авторизованного пользователя"""
        response = self.authorized_client.get(
            f'/profile/{self.user.username}/unfollow/', follow=True)
        self.assertRedirects(
            response,
            f'/profile/{self.user.username}/')
