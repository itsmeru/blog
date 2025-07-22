from rest_framework import status
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from questions.models import Question
from answers.models import Answer
from answers.serializers import (
    AnswerSerializer,
    AnswerCreateSerializer
)


class AnswerCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AnswerCreateSerializer,
        responses=AnswerSerializer,
        description="建立回答"
    )
    def post(self, request):
        serializer = AnswerCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        answer = serializer.save()
        answer_serializer = AnswerSerializer(answer, context={'request': request})
        return Response({
            "message": "留言發布成功",
            **answer_serializer.data
        }, status=status.HTTP_201_CREATED)


class AnswerListView(GenericAPIView):
    permission_classes = [AllowAny]

    def get(self, request, question_id=None):
        try:
            question = Question.objects.get(id=question_id)
            answers = Answer.objects.filter(question=question).order_by('-created_at')
            serializer = AnswerSerializer(answers, many=True, context={'request': request})
            return Response({
                "answers": serializer.data,
                "question": {
                    "id": question.id,
                    "title": question.title,
                    "content": question.content,
                    "author": question.author.username,
                    "views": question.views,
                    "likes": question.likes,
                    "created_at": question.created_at
                }
            })
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)


class AnswerDeleteView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, answer_id=None):
        try:
            answer = Answer.objects.get(id=answer_id)
            if answer.author != request.user:
                return Response({
                    "message": "您沒有權限刪除此回答"
                }, status=status.HTTP_403_FORBIDDEN)
            answer.delete()
            return Response({
                "message": "回答刪除成功"
            }, status=status.HTTP_200_OK)
        except Answer.DoesNotExist:
            return Response({
                "message": "回答不存在"
            }, status=status.HTTP_404_NOT_FOUND)


class AnswerLikeView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        try:
            answer = Answer.objects.get(id=pk)
            is_liked = answer.toggle_like(request.user)
            return Response({
                "message": "操作成功",
                "is_liked": is_liked,
                "likes": answer.likes
            }, status=status.HTTP_200_OK)
        except Answer.DoesNotExist:
            return Response({
                "message": "回答不存在"
            }, status=status.HTTP_404_NOT_FOUND)