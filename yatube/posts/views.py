from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from django.conf import settings

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post


def paginator(posts, request):
    paginator = Paginator(posts, settings.POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return {
        'page_obj': page_obj
    }


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('group', 'author')
    context = paginator(posts, request)
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    context = {
        'group': group
    }
    context.update(paginator(posts, request))
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.select_related('group')
    following = request.user.is_authenticated and Follow.objects.filter(
        user__username=request.user, author=author).exists()
    context = {
        'author': author,
        'following': following,
    }
    context.update(paginator(author_posts, request))
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
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    if form.is_valid():
        post = form.save()
        post.save()
        return redirect('posts:post_detail', post_id=post.id)

    return render(request, template, {
        'form': form,
        'post': post,
    })


@login_required
def add_comment(request, post_id):
    template = 'includes/comments.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
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
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    context = paginator(posts, request)
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    following = User.objects.get(username=username)
    if request.user != following:
        Follow.objects.get_or_create(user=request.user, author=following)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user, author=following).delete()
    return redirect('posts:profile', username=username)
