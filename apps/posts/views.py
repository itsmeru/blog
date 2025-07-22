from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema

from apps.posts.models import Post
from apps.posts.serializers import PostSerializer, PostCreateSerializer



@extend_schema(
    tags=["Posts"],
    request=PostCreateSerializer,
    responses=PostSerializer,
    description="建立貼文"
)
class PostListView(GenericAPIView):
    parser_classes = (FormParser,)
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        request=PostCreateSerializer,
        responses=PostSerializer,
        description="建立貼文"
    )
    def post(self, request):
        serializer = PostCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()
        return Response({
            "message": "貼文建立成功",
            "post_id": post.id
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["Posts"],
    request=PostCreateSerializer,
    responses=PostSerializer,
    description="查詢/更新/刪除單一貼文"
)
class PostDetailView(GenericAPIView):
    parser_classes = (FormParser,)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"message": "貼文不存在"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=PostCreateSerializer,
        responses=PostSerializer,
        description="修改貼文"
    )
    def patch(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({"message": "您沒有權限修改此貼文"}, status=status.HTTP_403_FORBIDDEN)
            serializer = PostCreateSerializer(post, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "貼文部分更新成功"}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "貼文不存在"}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=PostCreateSerializer,
        responses=PostSerializer,
        description="修改貼文"
    )
    def put(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({"message": "您沒有權限修改此貼文"}, status=status.HTTP_403_FORBIDDEN)
            serializer = PostCreateSerializer(post, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "貼文全量更新成功"}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "貼文不存在"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({"message": "您沒有權限刪除此貼文"}, status=status.HTTP_403_FORBIDDEN)
            post.delete()
            return Response({"message": "貼文刪除成功"}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({"message": "貼文不存在"}, status=status.HTTP_404_NOT_FOUND)
    