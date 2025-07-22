from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from posts.models import Post
from .serializers import PostSerializer, PostCreateSerializer


class PostCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

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


class PostDetailView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            serializer = PostSerializer(post, context={'request': request})
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({
                "message": "貼文不存在"
            }, status=status.HTTP_404_NOT_FOUND)


class PostDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id=None):
        try:
            post = Post.objects.get(id=post_id)
            if post.author != request.user:
                return Response({
                    "message": "您沒有權限刪除此貼文"
                }, status=status.HTTP_403_FORBIDDEN)
            post.delete()
            return Response({
                "message": "貼文刪除成功"
            }, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({
                "message": "貼文不存在"
            }, status=status.HTTP_404_NOT_FOUND)
    