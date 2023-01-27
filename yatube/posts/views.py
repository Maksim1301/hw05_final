from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow, User
from .utils import padinator_page


@cache_page(20, key_prefix='index_page')
def index(request):
    """"Главная страница"""
    text = 'Последние обновления на сайте'
    page_obj = padinator_page(Post.objects.all(), request)
    context = {
        'page_obj': page_obj,
        'text': text,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """"Страница группы постов"""
    group = get_object_or_404(Group, slug=slug)
    page_obj = padinator_page(Post.objects.filter(group=group),
                              request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """"Страница всех постов автора"""
    author = get_object_or_404(User, username=username)
    page_obj = padinator_page(Post.objects.filter(author=author).all(),
                              request)
    following_flag = False
    if (request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
            author=author).exists()):
        following_flag = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following_flag,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """"Страница редактирования постов"""
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """"Функция добавления поста"""
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """"Функция редактирования поста"""
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, "posts/create_post.html", context)


@login_required
def add_comment(request, post_id):
    """"Комментарии к посту в шаблоне post_detail"""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id) 


@login_required
def follow_index(request):
    """"Подписаться на автора"""
    text = 'Подписки пользователя'
    page_obj = padinator_page(
        Post.objects.filter(
            author__following__user=request.user),
        request)
    context = {
        'page_obj': page_obj,
        'text': text,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """"Подписаться на автора на странице автора"""
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user, author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """"Отписаться от автора"""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
