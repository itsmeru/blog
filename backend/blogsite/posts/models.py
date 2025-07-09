import base64

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
    
    def get_image_data_url(self):
        if self.image and isinstance(self.image, bytes):
            try:
                return f"data:{self.image_type};base64,{base64.b64encode(self.image).decode('utf-8')}"
            except Exception as e:
                print(f"圖片編碼錯誤: {e}")
        return None
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "image": self.get_image_data_url(),
            "author": self.author.username,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
        }
    
    @classmethod
    def create_post_with_image(cls, title, content, tags="", image_file=None, author=None):
        image_data = None
        image_type = None
        if image_file:
            image_data = image_file.read()
            image_type = image_file.content_type
        
        return cls.objects.create(
            title=title,
            content=content,
            tags=tags,
            image=image_data,
            image_type=image_type,
            author=author
        )
    
    @classmethod
    def get_posts(cls, page, size, keyword, order_by, tags=""):
        posts = cls.objects.all()
        
        if keyword:
            posts = posts.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if tag_list:
                tag_queries = Q()
                for tag in tag_list:
                    tag_queries |= Q(tags__icontains=tag)
                posts = posts.filter(tag_queries)
        
        posts = posts.order_by(order_by)
        paginator = Paginator(posts, size)
        posts_page = paginator.get_page(page)
        return posts_page
    
    @classmethod
    def get_posts_with_data(cls, page, size, keyword, order_by, tags=""):
        posts_page = cls.get_posts(page, size, keyword, order_by, tags)
        
        posts_data = []
        for post in posts_page:
            posts_data.append(post.to_dict())
        
        return {
            "posts": posts_data,
            "total": posts_page.paginator.count,
            "num_pages": posts_page.paginator.num_pages,
            "current_page": posts_page.number,
        }
