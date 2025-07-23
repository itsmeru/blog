from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema

from apps.questions.models import Question
from apps.questions.serializers import (
    QuestionSerializer,
    QuestionCreateSerializer,
)


@extend_schema(
    tags=["Questions"],
    request=QuestionCreateSerializer,
    responses=QuestionSerializer,
    description="建立問題"
)
class QuestionListView(GenericAPIView):
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        questions = Question.objects.all().order_by('-created_at')
        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        serializer = QuestionCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        return Response({
            "message": "問題發布成功",
            "question_id": question.id
        }, status=status.HTTP_201_CREATED)

@extend_schema(
    tags=["Questions"],
    request=QuestionCreateSerializer,
    responses=QuestionSerializer,
    description="查詢/更新/刪除單一問題"
)
class QuestionDetailView(GenericAPIView):
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question, context={'request': request})
            return Response(serializer.data)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionSerializer,
        description="建立問題"
    )
    def patch(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            if question.author != request.user:
                return Response({"message": "您沒有權限修改此問題"}, status=status.HTTP_403_FORBIDDEN)
            serializer = QuestionCreateSerializer(question, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "問題更新成功"}, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"message": "問題不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    @extend_schema(
        request=QuestionCreateSerializer,
        responses=QuestionSerializer,
        description="建立問題"
    )
    def put(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            if question.author != request.user:
                return Response({"message": "您沒有權限修改此問題"}, status=status.HTTP_403_FORBIDDEN)
            serializer = QuestionCreateSerializer(question, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"message": "問題全量更新成功"}, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"message": "問題不存在"}, status=status.HTTP_404_NOT_FOUND)
    
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

    @extend_schema(
        responses={
            200: {"description": "按讚操作成功"},
            404: {"description": "問題不存在"},
        },
        description="按讚/取消按讚問題",
        tags=["Questions"]
    )
    def post(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            is_liked = question.toggle_like(request.user)
            return Response({
                "success": True,
                "message": "操作成功",
                "data": {
                    "is_liked": is_liked,
                    "likes": question.likes
                }
            }, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({
                "success": False,
                "message": "問題不存在",
                "data": {}
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


