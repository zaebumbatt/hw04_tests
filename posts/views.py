from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm

import datetime


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        'page': page,
        'paginator': paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, "new.html", {"form": form})


def profile(request, username):
    user = User.objects.get(username=username)
    fullname = user.get_full_name()
    posts_count = Post.objects.filter(author=user).count()
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, 1)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'username': user,
        'fullname': fullname,
        'posts_count': posts_count,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    fullname = user.get_full_name()
    post = Post.objects.get(id=post_id)
    posts_count = Post.objects.filter(author=user).count()
    context = {
        'username': user,
        'fullname': fullname,
        'posts_count': posts_count,
        'post': post
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    user = User.objects.get(username=username)
    post = Post.objects.get(id=post_id)
    if post.author == request.user:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = user
                post.id = post_id
                post.pub_date = datetime.datetime.now()
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save()
                return redirect('post', username=user, post_id=post_id)
        else:
            form = PostForm(initial={'text': post.text, 'group': post.group})
    else:
        return redirect('index')
    return render(request, 'new.html', {'form': form, 'post': post})
