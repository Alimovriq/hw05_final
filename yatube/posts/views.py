from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_LIMIT

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post


# Пагинатор.
def paginator(posts, request):
    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }


# Главная страница.
def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('group', 'author')
    context = paginator(posts, request)
    return render(request, template, context)


# Посты, отфильтрованные по группам.
def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    context = {
        'group': group
    }
    context.update(paginator(posts, request))
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user_info = get_object_or_404(User, username=username)
    user_posts = user_info.posts.all()
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=user_info
        ).exists()
    else:
        following = False
    context = {
        'user_info': user_info,
        'following': following,
    }
    context.update(paginator(user_posts, request))
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post_info = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post_info.comments.all()
    context = {
        'post_info': post_info,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=request.user)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    is_edit = True
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    if form.is_valid():
        post = form.save()
        post.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(request, template, {
        'form': form,
        'post': post,
        'is_edit': is_edit})


@login_required
def add_comment(request, post_id):
    # Получите пост
    template = 'includes/comments.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('posts:post_detail', post_id=post_id)
    return render(request, template, {
        'form': form,
        'post': post
    }
    )


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    context = paginator(posts, request)
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    current_user = request.user
    following = User.objects.get(username=username)
    follower = Follow.objects.filter(user=current_user, author=following)
    if current_user != following and not follower.exists():
        Follow.objects.create(user=current_user, author=following)
    return redirect('posts:profile', username=current_user)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    current_user = request.user
    following = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=current_user, author=following)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=current_user)
