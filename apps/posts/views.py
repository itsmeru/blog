from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from apps.posts.serializers import (
    PostSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    PostSuccessResponseSerializer,
    PostListResponseSerializer,
)
from apps.posts.service import PostService
from core.app.base.serializer import BaseErrorSerializer, DeleteSuccessSerializer
from core.app.base.pagination import CustomPageNumberPagination


class PostCreateListView(GenericAPIView):
    parser_classes = (FormParser,)
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        responses={
            200: PostListResponseSerializer,
            400: BaseErrorSerializer,
        },
        summary="取得所有貼文",
        tags=["Posts"],
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                description="分頁頁數",
                default=1,
            ),
            OpenApiParameter(
                name="size",
                type=int,
                location=OpenApiParameter.QUERY,
                description="每頁筆數",
                default=10,
            ),
        ],
    )
    def get(self, request):
        queryset = PostService.list_posts()
        page = self.paginate_queryset(queryset)
        serializer = PostSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        request=PostCreateSerializer,
        responses={
            201: PostSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        summary="建立貼文",
        tags=["Posts"],
    )
    def post(self, request):
        post = PostService.create_post(request.data, request.user)
        return Response(
            {
                "success": True,
                "message": "貼文建立成功",
                "data": PostSerializer(post).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PostDetailView(GenericAPIView):
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if self.request.method == "GET":
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
        summary="查詢貼文",
        tags=["Posts"],
    )
    def get(self, request, post_id=None):
        post = PostService.get_post(post_id)
        return Response(
            {"success": True, "message": "查詢成功", "data": PostSerializer(post).data}
        )

    @extend_schema(
        request=PostUpdateSerializer,
        responses={
            200: PostSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="更新貼文",
        tags=["Posts"],
    )
    def patch(self, request, post_id=None):
        serializer = PostUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        post = PostService.update_post(
            post_id,
            request.user,
            serializer.validated_data,
            partial=True,
            files=request.FILES,
        )
        return Response(
            {
                "success": True,
                "message": "貼文更新成功",
                "data": PostSerializer(post, context={"request": request}).data,
            }
        )

    @extend_schema(
        responses={
            204: DeleteSuccessSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="刪除貼文",
        tags=["Posts"],
    )
    def delete(self, request, post_id=None):
        PostService.delete_post(post_id, request.user)
        return Response()
