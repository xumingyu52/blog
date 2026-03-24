from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Title, Context, Like, Collection, Comment
from .forms import TitleForm,ContextForm,CommentForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
import uuid
from django.utils import timezone
# 新增：导入登录装饰器和登录验证
from django.contrib.auth.decorators import login_required
# Create your views here.

def is_mobile(request):
    """检测是否为移动设备"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'phone']
    return any(k in user_agent for k in mobile_keywords)

def index(request):
    """论坛主页"""
    template = 'blog_context/mobile/index_mobile.html' if is_mobile(request) else 'blog_context/index.html'
    return render(request, template)

def posts(request):
    """帖子展示"""
    posts = Title.objects.order_by('-date_added')
    # 传递帖子直属用户
    
    context = {'posts': posts}
    template = 'blog_context/mobile/posts_mobile.html' if is_mobile(request) else 'blog_context/posts.html'
    return render(request, template, context)

def post(request, post_id):
    """帖子内容全部展示，包含评论和点赞交互"""
    post = get_object_or_404(Title, id=post_id)
    entries = post.context_set.all()
    
    # 评论逻辑：获取所有顶级评论（无父评论的）
    comments = Comment.objects.filter(post=post, parent_comment=None).order_by('-date_added')
    
    # 交互统计
    like_count = Like.get_like_count('article', post.id)
    collection_count = Collection.get_collection_count(post)
    
    # 用户状态
    is_liked = False
    is_collected = False
    liked_comment_ids = []
    liked_reply_ids = []
    if request.user.is_authenticated:
        is_liked = Like.get_user_like_status(request.user, 'article', post.id)
        is_collected = Collection.get_user_collection_status(request.user, post)
        liked_comment_ids = Like.objects.filter(user=request.user, content_type='comment').values_list('object_id', flat=True)
        liked_reply_ids = Like.objects.filter(user=request.user, content_type='reply').values_list('object_id', flat=True)
    
    comment_form = CommentForm()

    context = {
        'post': post, 
        'entries': entries,
        'comments': comments,
        'comment_form': comment_form,
        'like_count': like_count,
        'collection_count': collection_count,
        'is_liked': is_liked,
        'is_collected': is_collected,
        'liked_comment_ids': liked_comment_ids,
        'liked_reply_ids': liked_reply_ids,
    }
    template = 'blog_context/mobile/post_content_mobile.html' if is_mobile(request) else 'blog_context/post_content.html'
    return render(request, template, context)

@login_required
def new_post(request):
    """创建新帖子"""
    if request.method != "POST":
        title_form = TitleForm(prefix='title')
        context_form = ContextForm(prefix='context')
    else:
        title_form = TitleForm(request.POST, prefix='title')
        context_form = ContextForm(request.POST, request.FILES, prefix='context') 

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
    template = 'blog_context/mobile/new_post_mobile.html' if is_mobile(request) else 'blog_context/new_post.html'
    return render(request, template, context)

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
            context_form = ContextForm(request.POST, request.FILES, instance=context_obj, prefix='context')
        else:
            context_form = ContextForm(request.POST, request.FILES, initial={'title': title_obj}, prefix='context')

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



@login_required
def toggle_collection(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Title, id=post_id)
        action, count = Collection.toggle_collection(request.user, post)
        return JsonResponse({
            'status': 'success',
            'action': action,
            'collection_count': count,
        })
    return JsonResponse({'status': 'error', 'message': '无效请求'})


@login_required
def post_comment(request, post_id):
    post = get_object_or_404(Title, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user

            parent_comment_id = request.POST.get('parent_comment_id')
            if parent_comment_id:
                parent = Comment.objects.get(id=parent_comment_id)
                comment.parent_comment = parent
                
                # 获取回复给谁的名字
                reply_to_user_id = request.POST.get('reply_to_user_id')
                if reply_to_user_id:
                    comment.reply_to_id = reply_to_user_id
            comment.save()
            return redirect('blog_context:post', post_id=post_id)
    return redirect('blog_context:post', post_id=post_id)

@login_required
def collect_list(request):
    """收藏列表"""
    collections = Collection.objects.filter(user=request.user)
    template = 'blog_context/mobile/collect_list_mobile.html' if is_mobile(request) else 'blog_context/collect_list.html'
    return render(request, template, {'collections': collections})

@login_required
def upload_image(request):
    """处理Markdown图片上传"""
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        ext = image.name.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        today = timezone.now().strftime("%Y/%m/%d")
        path = f"post_images/{today}/{filename}"
        
        fs = FileSystemStorage()
        saved_filename = fs.save(path, image)
        url = fs.url(saved_filename)
        return JsonResponse({"success": 1, "url": url})
    return JsonResponse({"success": 0, "message": "上传失败"})
