from django.db import models
import uuid
from django.utils import timezone
# Create your models here.
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    pass

def avatar_upload_path(instance, filename):
    #生成一个随机的文件名
    ext = filename.split('.')[-1]
    return f'avatars/{timezone.now().strftime("%Y/%m/%d")}/{uuid.uuid4().hex}.{ext}'
class CustomUser(AbstractUser):
    #头像块
    avatar = models.ImageField(
        #上传后的存储路径
        upload_to=avatar_upload_path,
        #默认头像路径
        default='avatars/default.png',
        #允许用户暂时不上传图像
        blank = True,
        #后台管理显示的字段
        verbose_name='用户头像'
    )

    # 邮箱块
    email = models.EmailField(
        # 后台管理显示的字段名称
        verbose_name='电子邮箱',
        # 允许字段为空（表单提交时）
        blank=True,
        # 允许数据库中该字段为 NULL
        null=True,
        # 可选：添加唯一约束（如果需要），注释掉则允许多个用户用同一个邮箱
        # unique=True,
    )
    #邮箱块


    #指定用户管理器
    objects = CustomUserManager()

    class Meta:
        # verbose_name：后台管理中显示的单条数据名称（比如“用户”）
        verbose_name = '用户'
        # verbose_name_plural：后台管理中显示的多条数据名称（比如“用户列表”）
        verbose_name_plural = '用户'

    def get_initial(self):
        return self.username[0].upper() if self.username else '?'

    def get_avatar_color(self):
        # 根据用户名生成固定但看起来随机的颜色
        colors = [
            '#FF5733', '#33FF57', '#3357FF', '#F333FF', '#33FFF3',
            '#FF3385', '#FFB533', '#33FFB5', '#8533FF', '#FF3333',
            '#00A86B', '#8E44AD', '#2980B9', '#D35400', '#2C3E50'
        ]
        import hashlib
        # 使用哈希确保同一个用户总是得到同一个颜色
        hash_val = int(hashlib.md5(self.username.encode()).hexdigest(), 16)
        return colors[hash_val % len(colors)]

    def __str__(self):
        return self.username
    

    
