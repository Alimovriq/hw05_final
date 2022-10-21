# import shutil
# import tempfile

from django import forms
# from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Group, Post, Follow

# TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)
User = get_user_model()


# @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.post_1 = Post.objects.create(
            author=User.objects.create_user(username='Author_1',
                                            first_name='Иван',
                                            last_name='Иванов'),
            text='Тестовый пост от Author_1',
            group=Group.objects.create(
                title='Тестовая группа №1',
                slug='test_slug_1',
                description='Тестовое описание группы №1'
            ),
            image=uploaded
        )
        cls.comment_1 = Comment.objects.create(
            post=cls.post_1,
            author=cls.post_1.author,
            text='Комментарий 1'
        )
        cls.post_2 = Post.objects.create(
            author=User.objects.create_user(username='Author_2',
                                            first_name='Антон',
                                            last_name='Громов'),
            text='Тестовый пост от Author_2',
            group=Group.objects.create(
                title='Тестовая группа №2',
                slug='test_slug_2',
                description='Тестовое описание группы №2'
            ),
            image=uploaded
        )
        cls.comment_2 = Comment.objects.create(
            post=cls.post_2,
            author=cls.post_2.author,
            text='Комментарий 2'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование,
        # перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        # shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
        # Ссылаемся на пользователя (Автор, 'Author_1')
        self.user_author = self.post_1.author
        # Авторизуем пользователя (Автор, 'Author_1')
        self.author_client.force_login(self.user_author)

    def test_posts_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.post_1.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': self.post_1.author.username}):
                    'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post_1.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post_1.id}): 'posts/create_post.html'
        }

        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_show_correct_context_for_guest(self):
        """Шаблон index сформирован с правильным контекстом для Гостя."""
        response = self.guest_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(first_object.text,
                         self.post_2.text)
        self.assertEqual(first_object.image, self.post_2.image)
        # self.assertTrue(first_object.image, self.post_2.image)
        # self.assertEqual(first_object.image, 'posts/small.gif')
        # self.assertTrue(Post.objects.get(
        #     Post.objects.get(image='posts/small.gif')))

    def test_posts_index_show_correct_context_for_authorized_user(self):
        """Шаблон index сформирован
        с правильным контекстом для Авторизованного пользователя."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(first_object.text,
                         self.post_2.text),
        self.assertEqual(first_object.image, self.post_2.image)

    def test_posts_index_show_correct_context_for_author_user(self):
        """Шаблон index сформирован с правильным контекстом для Автора."""
        response = self.author_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(first_object.text,
                         self.post_2.text)
        self.assertEqual(first_object.image, self.post_2.image)

    def test_posts_group_list_show_correct_context_for_guest(self):
        """Шаблон group_list сформирован с правильным контекстом для Гостя."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': self.post_2.group.slug}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        posts = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(posts.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(group.title,
                         self.post_2.group.title)
        self.assertEqual(group.description,
                         self.post_2.group.description)
        self.assertEqual(posts.image, self.post_2.image)

    def test_posts_group_list_show_correct_context_for_authorized_user(self):
        """Шаблон group_list сформирован с
        правильным контекстом для Авторизованного пользователя."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.post_2.group.slug}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        posts = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(posts.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(group.title,
                         self.post_2.group.title)
        self.assertEqual(group.description,
                         self.post_2.group.description)
        self.assertEqual(posts.image, self.post_2.image)

    def test_posts_group_list_show_correct_context_for_author_user(self):
        """Шаблон group_list сформирован с правильным контекстом для Автора."""
        response = self.author_client.get(reverse('posts:group_list', kwargs={
            'slug': self.post_2.group.slug}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        posts = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(posts.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(group.title,
                         self.post_2.group.title)
        self.assertEqual(group.description,
                         self.post_2.group.description)
        self.assertEqual(posts.image, self.post_2.image)

    def test_posts_wrong_group_list(self):
        """Тест, чтобы пост не попал в другую группу."""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.post_1.group.slug}))
        posts = response.context['page_obj'][0]
        group = response.context['group']
        self.assertTrue(posts.author.first_name,
                        self.post_2.author.first_name)
        self.assertTrue(posts.text,
                        self.post_2.text)
        self.assertTrue(group.title,
                        self.post_2.group.title)
        self.assertTrue(group.description,
                        self.post_2.group.description)
        self.assertTrue(posts.image, self.post_2.image)

    def test_posts_profile_show_correct_context_for_guest_user(self):
        """Шаблон profile сформирован с правильным контекстом для Гостя."""
        response = self.guest_client.get(reverse('posts:profile', kwargs={
            'username': self.post_2.author.username}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        posts = response.context['page_obj'][0]
        author = response.context['author']
        self.assertEqual(author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(posts.image, self.post_2.image)

    def test_posts_profile_show_correct_context_for_authorized_user(self):
        """Шаблон profile сформирован с
        правильным контекстом для Авторизованного пользователя."""
        response = self.authorized_client.get(reverse('posts:profile', kwargs={
            'username': self.post_2.author.username}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        posts = response.context['page_obj'][0]
        author = response.context['author']
        self.assertEqual(author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(posts.image, self.post_2.image)

    def test_posts_profile_show_correct_context_for_author_user(self):
        """Шаблон profile сформирован с правильным контекстом для Автора."""
        response = self.author_client.get(reverse('posts:profile', kwargs={
            'username': self.post_2.author.username}))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        posts = response.context['page_obj'][0]
        author = response.context['author']
        self.assertEqual(author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(posts.image, self.post_2.image)

    def test_posts_post_detail_show_correct_context_for_guest_user(self):
        """Шаблон post_detail сформирован с правильным контекстом для Гостя."""
        response = self.guest_client.get(reverse('posts:post_detail', kwargs={
            'post_id': self.post_2.id}))
        posts = response.context['post_info']
        comments = response.context['comments'][0]
        self.assertEqual(posts.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(posts.image, self.post_2.image)
        self.assertEqual(comments.text, self.comment_2.text)

    def test_posts_post_detail_show_correct_context_for_authorized_user(self):
        """Шаблон post_detail сформирован с
        правильным контекстом для Авторизованного пользователя."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post_2.id}))
        posts = response.context['post_info']
        comments = response.context['comments'][0]
        self.assertEqual(posts.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(posts.image, self.post_2.image)
        self.assertEqual(comments.text, self.comment_2.text)

    def test_posts_post_detail_show_correct_context_for_author_user(self):
        """Шаблон post_detail сформирован с
        правильным контекстом для Автора."""
        response = self.author_client.get(reverse('posts:post_detail', kwargs={
            'post_id': self.post_2.id}))
        posts = response.context['post_info']
        comments = response.context['comments'][0]
        self.assertEqual(posts.author.first_name,
                         self.post_2.author.first_name)
        self.assertEqual(posts.text,
                         self.post_2.text)
        self.assertEqual(posts.image, self.post_2.image)
        self.assertEqual(comments.text, self.comment_2.text)

    def test_posts_edit_show_correct_context_for_author_user(self):
        """Шаблон create_page (edit) сформирован с
        правильным контекстом для Автора."""
        response = self.author_client.get(reverse('posts:post_edit', kwargs={
            'post_id': self.post_1.id}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_posts_create_post_show_correct_context_for_authorized_user(self):
        """Шаблон create_page (create) сформирован с
        правильным контекстом для Авторизованного пользователя."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_posts_create_post_page_show_correct_context_for_author_user(self):
        """Шаблон create_page (create) сформирован с
        правильным контекстом для Автора."""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    # Здесь создаются фикстуры: клиент и 15 тестовых записей.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_3 = User.objects.create_user(username='Author_3',
                                                first_name='Сергей',
                                                last_name='Петров',)
        cls.group_3 = Group.objects.create(
            title='Тестовая группа №3',
            slug='test_slug_3',
            description='Тестовое описание группы №3'
        )
        cls.posts = []
        for i in range(0, 15):
            cls.posts.append(Post(
                text=f"Тестовая надпись {i}",
                author=cls.author_3,
                group=cls.group_3
            )
            )
        Post.objects.bulk_create(cls.posts)

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
        # Ссылаемся на пользователя (Автор, 'Author_3')
        self.user_author = self.author_3
        # Авторизуем пользователя (Автор, 'Author_3')
        self.author_client.force_login(self.user_author)

    def test_first_page_contains_ten_records(self):
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('posts:index'): 'index',
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group_3.slug}): 'group_list',
            reverse('posts:profile', kwargs={
                'username': self.author_3.username}): 'profile',
        }
        for reverse_name in templates_pages_names.keys():
            response = self.client.get(reverse_name)
            self.assertEqual(len(
                response.context.get('page_obj').object_list), 10)

    def test_second_page_contains_five_records(self):
        # Проверка: на второй странице должно быть пять постов.
        templates_pages_names = {
            reverse('posts:index') + '?page=2': 'index',
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group_3.slug}) + '?page=2': 'group_list',
            reverse('posts:profile', kwargs={
                'username': self.author_3.username}) + '?page=2': 'profile',
        }
        for reverse_name in templates_pages_names.keys():
            response = self.client.get(reverse_name)
            self.assertEqual(len(
                response.context.get('page_obj').object_list), 5)


class CacheViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_1 = Post.objects.create(
            author=User.objects.create_user(username='Author_1',
                                            first_name='Иван',
                                            last_name='Иванов'),
            text='Тестовый пост от Author_1',
            group=Group.objects.create(
                title='Тестовая группа №1',
                slug='test_slug_1',
                description='Тестовое описание группы №1'
            ),
        )
        cls.comment_1 = Comment.objects.create(
            post=cls.post_1,
            author=cls.post_1.author,
            text='Комментарий 1'
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # self.user = User.objects.create_user(username='HasNoName')
        # # Создаем второй клиент
        # self.authorized_client = Client()
        # # Авторизуем этого пользователя (Не автор, 'HasNoName')
        # self.authorized_client.force_login(self.user)
        # # Создаем третий клиент
        # self.author_client = Client()
        # # Ссылаемся на пользователя (Автор, 'Author_1')
        # self.user_author = self.post_1.author
        # # Авторизуем пользователя (Автор, 'Author_1')
        # self.author_client.force_login(self.user_author)

    def test_posts_index_cache_for_guest(self):
        """Проверка кэширования на главной странице index."""
        response = self.guest_client.get(reverse('posts:index'))
        content_before = response.content
        # post_1 = self.post_1
        post = Post.objects.create(
            group=self.post_1.group,
            author=self.post_1.author,
            text='Текст для тестирования'
        )
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        content_after = response.content
        self.assertNotEqual(content_before, content_after)
        post.delete()
        response = self.guest_client.get(reverse('posts:index'))
        content_after_delete_post = response.content
        self.assertEqual(content_after, content_after_delete_post)
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        content_after_delete_cache = response.content
        self.assertNotEqual(
            content_after_delete_post, content_after_delete_cache)


class FollowViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_1 = Post.objects.create(
            author=User.objects.create_user(username='Author_1',
                                            first_name='Иван',
                                            last_name='Иванов'),
            text='Тестовый пост от Author_1',
            group=Group.objects.create(
                title='Тестовая группа №1',
                slug='test_slug_1',
                description='Тестовое описание группы №1'
            ),
        )
        cls.post_2 = Post.objects.create(
            author=User.objects.create_user(username='Author_2',
                                            first_name='Антон',
                                            last_name='Громов'),
            text='Тестовый пост от Author_2',
            group=Group.objects.create(
                title='Тестовая группа №2',
                slug='test_slug_2',
                description='Тестовое описание группы №2'
            ),
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

    def test_follow_for_authorized_user(self):
        """Авторизованный пользователь может подписаться."""
        # Посчитали подписчиков до подписки
        before = len(
            Follow.objects.all().filter(author_id=self.post_1.author.id))
        # Авторизованный пользователь пробует подписаться
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.post_1.author.username}))
        # Посчитали подписчиков после попытки подписаться пользователем
        after = len(
            Follow.objects.all().filter(author_id=self.post_1.author.id))
        self.assertEqual(after - 1, before)

    def test_unfollow_for_authorized_user(self):
        """Авторизованный пользователь может отписаться."""
        # Посчитали подписчиков до подписки
        before = len(
            Follow.objects.all().filter(author_id=self.post_1.author.id))
        # Авторизованный пользователь пробует подписаться и отписаться
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.post_1.author.username}))
        self.authorized_client.get(reverse('posts:profile_unfollow', kwargs={
            'username': self.post_1.author.username}))
        # Посчитали подписчиков после попытки отписаться пользователем
        after = len(
            Follow.objects.all().filter(author_id=self.post_1.author.id))
        self.assertEqual(after + 0, before)

    def test_view_posts_follow_for_authorized_user(self):
        """Подписанный пользователь может видеть ленту тех,
        на кого подписан и не может видеть тех, на кого не подписан."""
        self.authorized_client.get(reverse('posts:follow_index'))
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.post_1.author.username}))
        after_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        first_object = after_follow.context['page_obj'][0]
        response_no_follows = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(first_object.text, self.post_1.text)
        self.assertNotContains(response_no_follows, self.post_2.text)

    def test_follow_for_guest_user(self):
        """Гость не может подписаться."""
        # Посчитали подписчиков до подписки
        before = len(
            Follow.objects.all().filter(user_id=self.post_1.author.id))
        # Гость пробует подписаться
        self.guest_client.get(reverse('posts:profile_follow', kwargs={
            'username': self.post_1.author.username}))
        # Посчитали подписчиков после попытки подписаться Гостем
        after = len(Follow.objects.all().filter(user_id=self.post_1.author.id))
        self.assertEqual(after + 0, before)

    def test_unfollow_for_guest_user(self):
        """Гость не может отписаться."""
        # Посчитали подписчиков до подписки
        before = len(
            Follow.objects.all().filter(user_id=self.post_1.author.id))
        # Гость пробует отписаться
        self.guest_client.get(reverse('posts:profile_unfollow', kwargs={
            'username': self.post_1.author.username}))
        # Посчитали подписчиков после попытки отписаться Гостем
        after = len(Follow.objects.all().filter(user_id=self.post_1.author.id))
        self.assertEqual(after + 0, before)
