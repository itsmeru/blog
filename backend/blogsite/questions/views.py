from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter

from questions.models import Question
from questions.serializers import (
    QuestionSerializer,
    QuestionCreateSerializer,
)


class QuestionCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionSerializer,
        description="建立問題"
    )
    def post(self, request):
        serializer = QuestionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        return Response({
            "message": "問題發布成功",
            "question_id": question.id
        }, status=status.HTTP_201_CREATED)


class QuestionDetailView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question, context={'request': request})
            return Response(serializer.data)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)


class QuestionDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            if question.author != request.user:
                return Response({
                    "message": "您沒有權限刪除此問題"
                }, status=status.HTTP_403_FORBIDDEN)
            question.delete()
            return Response({
                "message": "問題刪除成功"
            }, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)


class QuestionLikeView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            is_liked = question.toggle_like(request.user)
            return Response({
                "message": "操作成功",
                "is_liked": is_liked,
                "likes": question.likes
            }, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)


class QuestionViewView(GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            question.increment_views()
            return Response({
                "message": "瀏覽次數更新成功",
                "views": question.views
            }, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)