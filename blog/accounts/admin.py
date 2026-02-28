from django.contrib import admin
from .models import CustomUser

# Register your models here.
# 注册：只是让后台能管理
admin.site.register(CustomUser)