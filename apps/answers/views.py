from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import FormParser

from apps.answers.serializers import (
    AnswerSerializer,
    AnswerCreateSerializer,
    AnswerListResponseSerializer,
    AnswerSuccessResponseSerializer,
    AnswerLikeSuccessResponseSerializer,
)
from apps.answers.service import AnswerService
from core.app.base.serializer import BaseErrorSerializer, DeleteSuccessSerializer


class AnswerCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser,)

    @extend_schema(
        request=AnswerCreateSerializer,
        responses={
            201: AnswerSuccessResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="建立回答",
        tags=["Answers"],
    )
    def post(self, request):
        answer = AnswerService.create_answer(request.data, request.user)
        return Response(
            {
                "success": True,
                "message": "留言發布成功",
                "data": AnswerSerializer(answer).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AnswerListView(GenericAPIView):
    permission_classes = [AllowAny]
    parser_classes = (FormParser,)

    @extend_schema(
        responses={
            200: AnswerListResponseSerializer,
            400: BaseErrorSerializer,
        },
        description="取得所有回答",
        tags=["Questions"],
    )
    def get(self, request, question_id=None):
        answers, is_liked_map = AnswerService.list_answers(question_id, request.user)
        serializer = AnswerSerializer(answers, many=True, context={"request": request})
        answers_data = serializer.data
        for ans in answers_data:
            ans["is_liked"] = is_liked_map.get(ans["id"], False)
        return Response({"success": True, "message": "查詢成功", "data": answers_data})


class AnswerDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser,)

    @extend_schema(
        request=AnswerCreateSerializer,
        responses={
            200: AnswerSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="更新回答",
        tags=["Answers"],
    )
    def put(self, request, answer_id=None):
        serializer = AnswerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = AnswerService.update_answer(
            answer_id, request.user, serializer.validated_data, partial=False
        )
        return Response(
            {
                "success": True,
                "message": "更新成功",
                "data": AnswerSerializer(answer).data,
            }
        )

    @extend_schema(
        request=AnswerCreateSerializer,
        responses={
            200: AnswerSuccessResponseSerializer,
            400: BaseErrorSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="部分更新回答",
        tags=["Answers"],
    )
    def patch(self, request, answer_id=None):
        serializer = AnswerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answer = AnswerService.update_answer(
            answer_id, request.user, serializer.validated_data, partial=True
        )
        return Response(
            {
                "success": True,
                "message": "更新成功",
                "data": AnswerSerializer(answer).data,
            }
        )

    @extend_schema(
        request=AnswerCreateSerializer,
        responses={
            204: DeleteSuccessSerializer,
            403: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        description="刪除回答",
        tags=["Answers"],
    )
    def delete(self, request, answer_id=None):
        AnswerService.delete_answer(answer_id, request.user)
        return Response()


@extend_schema(
    responses={
        200: AnswerLikeSuccessResponseSerializer,
        400: BaseErrorSerializer,
        404: BaseErrorSerializer,
    },
    description="按讚/取消按讚回答",
    tags=["Answers"],
)
class AnswerLikeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (FormParser,)

    def post(self, request, answer_id=None):
        answer, is_liked = AnswerService.toggle_like(answer_id, request.user)
        return Response(
            {
                "success": True,
                "message": "操作成功",
                "data": {"is_liked": is_liked, "likes": answer.likes},
            }
        )
