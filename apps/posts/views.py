from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import FormParser
from drf_spectacular.utils import extend_schema

from apps.posts.serializers import (
    PostSerializer, 
    PostCreateSerializer,
    PostSuccessResponseSerializer,
    PostListResponseSerializer
)
from apps.posts.service import PostService
from core.app.base.serializer import BaseErrorSerializer, DeleteSuccessSerializer

class PostCreateListView(GenericAPIView):
    parser_classes = (FormParser,)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
    responses={
        200: PostListResponseSerializer,
        400: BaseErrorSerializer,
    },
    description="取得所有貼文",
    tags=["Posts"]
)
    def get(self, request):
        posts = PostService.list_posts()
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response({
            "success": True,
            "message": "查詢成功",
            "data": serializer.data
        })
    
    @extend_schema(
        request=PostCreateSerializer,
        responses={
            201: PostSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="建立貼文",
        tags=["Posts"]
    )
    def post(self, request):
        post = PostService.create_post(request.data, request.user)
        return Response({
            "success": True,
            "message": "貼文建立成功",
            "data": PostSerializer(post).data
        }, status=status.HTTP_201_CREATED)


class PostDetailView(GenericAPIView):
    parser_classes = (FormParser,)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        request=PostCreateSerializer,
        responses={
            200: PostSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="查詢貼文", 
        tags=["Posts"]
    )
    def get(self, request, post_id=None):
        post = PostService.get_post(post_id)
        return Response({
            "success": True,
            "message": "查詢成功",
            "data": PostSerializer(post).data
        })

    @extend_schema(
        request=PostCreateSerializer,
        responses={
            200: PostSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="部分更新貼文",
        tags=["Posts"]
    )
    def patch(self, request, post_id=None):
        post = PostService.update_post(post_id, request.user, request.data, partial=True)
        return Response({
            "success": True,
            "message": "貼文部分更新成功",
            "data": PostSerializer(post).data
        })

    @extend_schema(
        request=PostCreateSerializer,
        responses={
            200: PostSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="全量更新貼文",
        tags=["Posts"]
    )
    def put(self, request, post_id=None):
        post = PostService.update_post(post_id, request.user, request.data, partial=False)
        return Response({
            "success": True,
            "message": "貼文全量更新成功",
            "data": PostSerializer(post).data
        })

    @extend_schema(
        responses={
            204: DeleteSuccessSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="刪除貼文",
        tags=["Posts"]
    )
    def delete(self, request, post_id=None):
        PostService.delete_post(post_id, request.user)
        return Response()
    