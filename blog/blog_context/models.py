from django.db import models
#导入自定义用户模型
from accounts.models import CustomUser
from django.utils import timezone


# Create your models here.

class Title(models.Model):
    """用户创建的文章标题数据结构"""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    #默认为管理员
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='作者', default=1)

    def __str__(self):
        """模型表示方法"""
        return self.text
    
class Context(models.Model):
    """帖子文章内容"""
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        """用于存储模型的额外信息"""
        verbose_name_plural = 'contexts'

    def __str__(self):
        """返回一个表示内容的略写内容"""
        return f"{self.text[:150]}..."

#通用点赞模型
class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes', verbose_name='点赞用户')

    #点赞对象类型
    content_type = models.CharField(
        max_length = 20,
        verbose_name='点赞对象类型',
        choices=[
            ('article','文章'),
            ('comment','评论'),
            ('reply','回复'),
        ],
        default='article',
    )
    object_id = models.PositiveIntegerField(verbose_name='对象ID')

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
        unique_together = ('user', 'content_type', 'object_id')

        #索引优化
        indexes = [
            models.Index(fields=['content_type','object_id'], name='idx_like_content'),
            models.Index(fields=['user','content_type'], name='idx_like_user_content'),
        ]
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.content_type} {self.object_id}"

    @classmethod
    def get_like_count(cls, content_type, object_id):
        """获取某个对象的所有点赞数量"""
        return cls.objects.filter(content_type=content_type, object_id=object_id).count()

    @classmethod
    def get_user_like_status(cls, user, content_type, object_id):
        """获取用户对某个对象是否点赞"""
        return cls.objects.filter(user=user, content_type=content_type, object_id=object_id).exists()

    @classmethod
    def toggle_like(cls, user, content_type, object_id):
        """切换点赞状态"""
        like, created = cls.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id,
        )
        if not created:
            like.delete()
            return "cancel", cls.get_like_count(content_type, object_id)
        else:
            return "like", cls.get_like_count(content_type, object_id)

#收藏数据模型
class Collection(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='collections')
    post = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='collections')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        verbose_name = '收藏'
        verbose_name_plural = '收藏'
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.post.text[:20]}..."

    @classmethod
    def get_collection_count(cls, post):
        """获取某个帖子的收藏数量"""
        return cls.objects.filter(post=post).count()
    
    @classmethod
    def get_user_collection_status(cls, user, post):
        """获取用户对某个帖子的收藏状态"""
        return cls.objects.filter(user=user, post=post).exists()
    
    @classmethod
    def toggle_collection(cls, user, post):
        """切换收藏状态"""
        collection, created = cls.objects.get_or_create(
            user=user,
            post=post,
        )
        if not created:
            collection.delete()
            return "cancel", cls.get_collection_count(post)
        else:
            return "collect", cls.get_collection_count(post)

#评论数据模型
class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    #回复
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True,
    )

    # 回复给谁
    reply_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name='received_replies',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
    def __str__(self):
        return f"{self.user.username} 评论了 {self.post.text[:20]}..."
