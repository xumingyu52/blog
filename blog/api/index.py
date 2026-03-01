import os
import sys

# 把 Django 项目目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')

from django.core.wsgi import get_wsgi_application

# Vercel 需要一个叫 handler 的变量
handler = get_wsgi_application()
