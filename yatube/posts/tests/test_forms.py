import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = User.objects.create_user(username='Author_5',
                                              first_name='Иван',
                                              last_name='Иванов')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа №1',
            slug='test_slug_1',
            description='Тестовое описание группы №1')
        cls.group_2 = Group.objects.create(
            title='Тестовая группа №2',
            slug='test_slug_2',
            description='Тестовое описание группы №2')
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование,
        # перемещение, изменение папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем этого пользователя (Не автор, 'HasNoName')
        self.authorized_client.force_login(self.user)

    def test_create_img_post_authorized_user(self):
        """Пост с изображением созданный Авторизованным юзером."""
        posts_count = Post.objects.count()
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
            'group': self.group_1.id,
            'text': 'Запись от Авторизованного юзера',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group_1,
                image="posts/small.gif"
            ).exists()
        )

    def test_create_post_authorized_user(self):
        """Пост созданный Авторизованным юзером."""
        posts_count = Post.objects.count()
        form_data = {
            'group': self.group_1.id,
            'text': 'Запись от Авторизованного юзера',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group_1
            ).exists()
        )
        post_id = Post.objects.get(id=self.group_1.id)
        self.assertEqual(User.objects.get(
            posts=post_id.id).username, self.user.username)
        self.assertEqual(Group.objects.get(
            posts=post_id.id).title, self.group_1.title)
        self.assertEqual(Post.objects.get(id=self.group_1.id).text,
                         form_data['text'])

    def test_edit_post_authorized_user(self):
        """Пост отредактированный авторизованным пользователем."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Запись от Авторизованного юзера',
            'group': self.group_1.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_id = Post.objects.get(id=self.group_1.id)
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': post_id.id}), {
                    'text': 'Отредактированный текст',
                    'group': self.group_2.id,
            })
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id.id}))
        self.assertEqual(Post.objects.get(id=post_id.id).text,
                         'Отредактированный текст')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertFalse(Post.objects.filter(
            text=form_data['text'],
            group=self.group_1
        ).exists()
        )
        # self.assertFalse(Post.objects.filter(
        #     text=form_data['text'],
        #     group=self.group_1
        # ).exists()
        # )

    def test_create_post_guest_user(self):
        """Пост не созданный Гостем."""
        form_data = {
            'group': self.group_1.id,
            'text': 'Запись от Гостя',
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group_1
            ).exists()
        )

    def test_create_img_post_guest_user(self):
        """Пост с изображением не созданный Гостем."""
        posts_count = Post.objects.count()
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
            'group': self.group_1.id,
            'text': 'Запись от Гостя',
            'image': uploaded,
        }
        # Отправляем POST-запрос
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group_1,
                image="posts/small.gif"
            ).exists()
        )

    def test_create_comment_authorized_user(self):
        """Комментарий созданный Авторизованным юзером."""
        # переменная для подсчета комментов
        comments_count = Comment.objects.count()
        # создаем новый пост , который будем комментить
        form_data = {
            'text': 'Запись от Авторизованного юзера',
            'group': self.group_1.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_id = Post.objects.get(id=self.group_1.id)
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': post_id.id}), {
                    'text': 'Комментарий',
            })
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post_id.id}))
        self.assertEqual(Comment.objects.get(id=post_id.id).text,
                         'Комментарий')
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_create_comment_guest_user(self):
        """Комментарий не созданный Гостем."""
        # переменная для подсчета комментов
        comments_count = Comment.objects.count()
        # создаем новый пост , который будем комментить
        form_data = {
            'text': 'Запись от Авторизованного юзера',
            'group': self.group_1.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        post_id = Post.objects.get(id=self.group_1.id)
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={
                'post_id': post_id.id}), {
                    'text': 'Комментарий гостя',
            })
        self.assertEqual(Comment.objects.count(), comments_count + 0)
        self.assertFalse(
            Comment.objects.filter(
                text='Комментарий гостя',
            ).exists())
