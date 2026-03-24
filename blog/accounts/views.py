from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog_context.models import Title
from .models import CustomUser
from blog_context.views import is_mobile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog_context:posts')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', context={'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('blog_context:posts')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('blog_context:posts')
    else:
        form = AuthenticationForm()
    template = 'accounts/mobile/login_mobile.html' if is_mobile(request) else 'accounts/login.html'
    return render(request, template, {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人资料已更新！')
            return redirect('accounts:user_profile', user_id=request.user.id)
    else:
        form = CustomUserChangeForm(instance=request.user)
    template = 'accounts/mobile/edit_profile_mobile.html' if is_mobile(request) else 'accounts/edit_profile.html'
    return render(request, template, {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 保持登录状态
            messages.success(request, '密码已修改成功！')
            return redirect('accounts:user_profile', user_id=request.user.id)
    else:
        form = CustomPasswordChangeForm(request.user)
    template = 'accounts/mobile/change_password_mobile.html' if is_mobile(request) else 'accounts/change_password.html'
    return render(request, template, {'form': form})

def user_profile(request, user_id):
    profile_user = get_object_or_404(CustomUser, id=user_id)
    user_posts = Title.objects.filter(author=profile_user).order_by('-date_added')
    context = {
        'profile_user': profile_user,
        'user_posts': user_posts,
    }
    template = 'accounts/mobile/profile_mobile.html' if is_mobile(request) else 'accounts/profile.html'
    return render(request, template, context)
