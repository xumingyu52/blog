#!/bin/bash
# Vercel 构建脚本：安装依赖 + 收集静态文件

pip install -r requirements.txt
python manage.py collectstatic --noinput
