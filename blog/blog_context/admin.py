from django.contrib import admin
from .models import Title, Context, Comment, Like, Collection

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'date_added', 'text_excerpt')
    list_filter = ('date_added', 'user')
    search_fields = ('text', 'user__username', 'post__text')

    def text_excerpt(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_excerpt.short_description = '内容摘要'

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'date_added')
    search_fields = ('text', 'author__username')

@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ('title', 'text_excerpt', 'date_added')
    
    def text_excerpt(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_excerpt.short_description = '内容摘要'

admin.site.register(Like)
admin.site.register(Collection)

