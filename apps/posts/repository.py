from apps.posts.models import Post
from django.core.paginator import Paginator
from django.db.models import Q


class PostRepository:
    @staticmethod
    def get_by_id(post_id):
        return Post.objects.filter(id=post_id).first()

    @staticmethod
    def get_all_posts():
        return Post.objects.all().order_by("-created_at")

    @staticmethod
    def get_posts_with_filters(page, size, keyword, tags=""):
        posts = Post.objects.all()

        if keyword:
            posts = posts.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )

        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
            if tag_list:
                tag_queries = Q()
                for tag in tag_list:
                    tag_queries |= Q(tags__icontains=tag)
                posts = posts.filter(tag_queries)

        paginator = Paginator(posts, size)
        return paginator.get_page(page)

    @staticmethod
    def create_post(title, content, author, tags="", image_file=None):
        return Post.objects.create(
            title=title,
            content=content,
            author=author,
            tags=tags,
            image=image_file,
        )

    @staticmethod
    def update_post(post, data, partial=False):
        if partial:
            for field, value in data.items():
                if hasattr(post, field):
                    setattr(post, field, value)
        else:
            for field, value in data.items():
                if hasattr(post, field):
                    setattr(post, field, value)
        post.save()
        return post

    @staticmethod
    def delete_post(post):
        post.delete()
        return True
