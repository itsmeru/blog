from apps.posts.repository import PostRepository
from apps.posts.serializers import PostCreateSerializer
from rest_framework.exceptions import NotFound, PermissionDenied


class PostService:
    repository_class = PostRepository

    @classmethod
    def create_post(cls, data, user):
        serializer = PostCreateSerializer(
            data=data, context={"request": {"user": user}}
        )
        serializer.is_valid(raise_exception=True)
        post = cls.repository_class.create_post(
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            author=user,
            tags=serializer.validated_data.get("tags", ""),
            image_file=serializer.validated_data.get("image"),
        )
        return post

    @classmethod
    def list_posts(cls, page=1, size=10, keyword=None, tags=None):
        posts = cls.repository_class.get_posts_with_filters(
            page, size, keyword, tags or ""
        )
        return posts

    @classmethod
    def get_post(cls, post_id):
        post = cls.repository_class.get_by_id(post_id)
        if not post:
            raise NotFound("貼文不存在")
        return post

    @classmethod
    def update_post(cls, post_id, user, data, partial=False, files=None):
        post = cls.repository_class.get_by_id(post_id)
        if not post:
            raise NotFound("貼文不存在")
        if post.author != user:
            raise PermissionDenied("您沒有權限修改此貼文")
        # 直接將 image 欄位設為檔案物件
        if files and 'image' in files:
            data['image'] = files['image']
        elif 'image' in data and data['image'] is None:
            data['image'] = None
        post = cls.repository_class.update_post(post, data, partial=partial)
        return post

    @classmethod
    def delete_post(cls, post_id, user):
        post = cls.repository_class.get_by_id(post_id)
        if not post:
            raise NotFound("貼文不存在")
        if post.author != user:
            raise PermissionDenied("您沒有權限刪除此貼文")

        return cls.repository_class.delete_post(post)
