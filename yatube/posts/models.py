from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы')
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес группы')
    description = models.TextField(
        verbose_name='Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
        blank=False)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарии',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария',
        blank=False)
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор для подписчиков',
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
