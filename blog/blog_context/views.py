from django.shortcuts import render, redirect
from .models import Title, Context, Like, Collection, Comment
from .forms import TitleForm,ContextForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
# 新增：导入登录装饰器和登录验证
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    """论坛主页"""
    return render(request, 'blog_context/index.html')

def posts(request):
    """帖子展示"""
    posts = Title.objects.order_by('-date_added')
    # 传递帖子直属用户
    
    context = {'posts': posts}
    return render(request, 'blog_context/posts.html', context)

def post(request, post_id):
    """帖子内容全部展示"""
    post = Title.objects.get(id=post_id)
    entries = post.context_set.all()
    context = {'post': post, 'entries': entries}
    return render(request, 'blog_context/post_content.html', context)

@login_required
def new_post(request):
    """创建新帖子"""
    if request.method != "POST":
        title_form = TitleForm(prefix='title')
        context_form = ContextForm(prefix='context')
    else:
        title_form = TitleForm(request.POST, prefix='title')
        context_form = ContextForm(request.POST, prefix='context') 

        if title_form.is_valid() and context_form.is_valid():
            title_instance = title_form.save(commit=False)
            title_instance.author = request.user
            title_instance.save()

            context_instance = context_form.save(commit=False)
            context_instance.title = title_instance
            context_instance.save()
            return redirect('blog_context:posts')
        
    context = {
        'title_form': title_form,
        'context_form': context_form,
    }
    return render(request, 'blog_context/new_post.html', context)

@login_required
def edit_post(request, post_id):
    """编辑已有的帖子"""
    title_obj = get_object_or_404(Title, id = post_id)
    context_obj = title_obj.context_set.filter().first()
    
    if request.user.is_authenticated and title_obj.author != request.user:
        messages.error(request, '你没有权限编辑这个帖子')
        return redirect('blog_context:post', post_id=post_id)
    if request.method != 'POST':
        title_form = TitleForm(instance=title_obj ,prefix='title')
        context_form = ContextForm(instance=context_obj, prefix='context')
    else:
        # 4. 处理POST请求（提交表单，带prefix）
        title_form = TitleForm(request.POST, instance=title_obj, prefix='title')
        # 提交内容时，需要绑定title外键（context_obj为None时，手动传initial）
        if context_obj:
            context_form = ContextForm(request.POST, instance=context_obj, prefix='context')
        else:
            context_form = ContextForm(request.POST, initial={'title': title_obj}, prefix='context')

        # 验证并保存
        if title_form.is_valid() and context_form.is_valid():
            title_form.save()
            new_context = context_form.save(commit=False)
            if not context_obj:
                new_context.title = title_obj
            new_context.save()
            messages.success(request, '帖子编辑成功！')
            return redirect('blog_context:post', post_id=post_id)  # 保存后跳转

    return render(request, 'blog_context/edit_post.html', {
        'title_form': title_form,
        'context_form': context_form,
        'post_id': post_id
    })

@login_required
def toggle_like(request):
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        object_id = request.POST.get('object_id')

        result, like_count = Like.toggle_like(request.user, content_type, object_id)
        
        return JsonResponse({
            'status': 'success',
            'action': result,
            'like_count': like_count,
        })
    return JsonResponse({'status': 'error', 'message': '无效请求'})




