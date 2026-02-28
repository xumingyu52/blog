"""为应用程序accounts定义url模式"""

from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
app_name = "accounts"

urlpatterns = [
    path('login/', views.user_login, name='login'),
    #包含默认身份验证的url
    path('',include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page='blog_context:posts'), name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='password_change'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
]