from apps.posts.repository import PostRepository
from apps.posts.serializers import PostCreateSerializer
from rest_framework.exceptions import NotFound, PermissionDenied


class PostService:
    @staticmethod
    def create_post(data, user):
        serializer = PostCreateSerializer(
            data=data, context={"request": {"user": user}}
        )
        serializer.is_valid(raise_exception=True)

        image_file = serializer.validated_data.get("image")
        post = PostRepository.create_post(
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            author=user,
            tags=serializer.validated_data.get("tags", ""),
            image_file=image_file,
        )
        return post

    @staticmethod
    def list_posts(page=1, size=10, keyword=None, tags=None):
        posts = PostRepository.get_posts_with_filters(page, size, keyword, tags or "")
        return posts

    @staticmethod
    def get_post(post_id):
        post = PostRepository.get_by_id(post_id)
        if not post:
            raise NotFound("貼文不存在")
        return post

    @staticmethod
    def update_post(post_id, user, data, partial=False):
        post = PostRepository.get_by_id(post_id)
        if not post:
            raise NotFound("貼文不存在")
        if post.author != user:
            raise PermissionDenied("您沒有權限修改此貼文")

        # 處理圖片檔案
        image_file = data.get("image")
        if image_file:
            data["image"] = image_file

        post = PostRepository.update_post(post, data, partial=partial)
        return post

    @staticmethod
    def delete_post(post_id, user):
        post = PostRepository.get_by_id(post_id)
        if not post:
            raise NotFound("貼文不存在")
        if post.author != user:
            raise PermissionDenied("您沒有權限刪除此貼文")

        return PostRepository.delete_post(post)
