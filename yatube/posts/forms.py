from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Текст поста',
                  'image': 'Картинка'}
        help_texts = {'group': 'Выберите группу (Необязательное поле)',
                      'text': 'Введите текст поста (Обязательное поле)',
                      'image': 'Загрузите картинку (Необязательное поле)',
                      }
        fields = ["text", "group", "image"]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Текст комментария'}
        help_texts = {'text': 'Введите текст поста (Обязательное поле)'}
        fields = ["text"]
