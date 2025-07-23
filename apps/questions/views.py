from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter

from apps.questions.serializers import (
    QuestionSerializer,
    QuestionCreateSerializer,
    QuestionSuccessResponseSerializer,
    QuestionListResponseSerializer,
)
from apps.questions.service import QuestionService
from core.app.base.serializer import BaseErrorSerializer, DeleteSuccessSerializer
from core.app.base.pagination import CustomPageNumberPagination


class QuestionCreateListView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)
    pagination_class = CustomPageNumberPagination

    @extend_schema(
        responses={
            200: QuestionListResponseSerializer,
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="取得所有問題",
        tags=["Questions"],
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
        queryset = QuestionService.list_questions()
        page = self.paginate_queryset(queryset)
        serializer = QuestionSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @extend_schema(
        request=QuestionCreateSerializer,
        responses={
            201: QuestionSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        summary="建立問題",
        tags=["Questions"],
    )
    def post(self, request):
        question = QuestionService.create_question(request.data, request.user)
        return Response(
            {
                "success": True,
                "message": "問題發布成功",
                "data": QuestionSerializer(question).data,
            },
            status=status.HTTP_201_CREATED,
        )


class QuestionDetailView(GenericAPIView):
    parser_classes = (FormParser,)

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        responses={
            200: QuestionSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="查詢問題",
        tags=["Questions"],
    )
    def get(self, request, question_id=None):
        question = QuestionService.get_question(question_id)
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": QuestionSerializer(question).data,
            }
        )

    @extend_schema(
        request=QuestionCreateSerializer,
        responses={
            200: QuestionSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="更新問題",
        tags=["Questions"],
    )
    def patch(self, request, question_id=None):
        question = QuestionService.update_question(
            question_id, request.user, request.data, partial=True
        )
        return Response(
            {
                "success": True,
                "message": "問題更新成功",
                "data": QuestionSerializer(question).data,
            }
        )

    @extend_schema(
        responses={
            204: DeleteSuccessSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="刪除問題",
        tags=["Questions"],
    )
    def delete(self, request, question_id=None):
        QuestionService.delete_question(question_id, request.user)
        return Response()


class QuestionLikeView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: {"description": "按讚操作成功"},
            404: {"description": "問題不存在"},
        },
        summary="按讚/取消按讚問題",
        tags=["Questions"],
    )
    def post(self, request, question_id=None):
        question, is_liked = QuestionService.toggle_like(question_id, request.user)
        return Response(
            {
                "success": True,
                "message": "操作成功",
                "data": {"is_liked": is_liked, "likes": question.likes},
            }
        )


class QuestionViewView(GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: QuestionSuccessResponseSerializer,
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        summary="更新問題瀏覽次數",
        tags=["Questions"],
    )
    def post(self, request, question_id=None):
        question = QuestionService.increment_views(question_id)
        return Response(
            {
                "success": True,
                "message": "瀏覽次數更新成功",
                "data": {"views": question.views},
            }
        )
