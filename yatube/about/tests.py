from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AboutUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_for_all(self):
        """Страницы / доступные любому пользователю."""
        urls = {
            '/about/author/',
            '/about/tech/',
        }
        for address in urls:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
