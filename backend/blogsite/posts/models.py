from accounts.models import Account
from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.CharField(max_length=100, null=True, blank=True)
    image = models.BinaryField(null=True, blank=True)
    image_type = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    @classmethod
    def get_posts(cls, page, size, keyword, order_by, tags=""):
        posts = cls.objects.all()
        
        # 關鍵字搜尋
        if keyword:
            posts = posts.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        
        # 標籤篩選
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if tag_list:
                # 使用 Q 物件來實現 OR 查詢（包含任一標籤的貼文）
                tag_queries = Q()
                for tag in tag_list:
                    tag_queries |= Q(tags__icontains=tag)
                posts = posts.filter(tag_queries)
        
        posts = posts.order_by(order_by)
        paginator = Paginator(posts, size)
        posts_page = paginator.get_page(page)
        return posts_page
