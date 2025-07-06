from accounts.models import Account
from django.db import models


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)

    def create(self, title, content, author):
        post = Post(title=title, content=content, author=author)
        post.save()
