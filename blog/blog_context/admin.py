from django.contrib import admin

# Register your models here.
from .models import Title, Context

admin.site.register(Title)
admin.site.register(Context)

