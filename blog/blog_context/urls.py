"""定义blog_context的URL模式"""

from django.urls import path

from . import views

app_name  = 'blog_context'

urlpatterns = [
    #主页
    path('', views.index, name = 'index'),
    #显示所有帖子
    path('posts/', views.posts, name = 'posts'),
    #显示帖子内容
    path('posts/<int:post_id>', views.post, name = 'post'),
    #新增新的帖子
    path('new_post/',views.new_post, name = 'new_post'),
    #编辑帖子
    path('edit_post/<int:post_id>/', views.edit_post, name = 'edit_post'),
    #功能性接口
    path('toggle_like/', views.toggle_like, name='toggle_like'),
    path('toggle_collection/', views.toggle_collection, name='toggle_collection'),
    path('posts/<int:post_id>/comment/', views.post_comment, name='post_comment'),
    path('collections/', views.collect_list, name='collect_list'),
]