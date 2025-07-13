from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from questions.models import Question
from answers.models import Answer
from answers.serializers import (
    AnswerSerializer,
    AnswerCreateSerializer
)


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return AnswerCreateSerializer
        return AnswerSerializer

    def list(self, request):
        question_id = request.query_params.get('question_id')
        if not question_id:
            return Response({
                "message": "請提供問題ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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

    def create(self, request):
        question_id = request.data.get('question_id')
        if not question_id:
            return Response({
                "message": "請提供問題ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            question = Question.objects.get(id=question_id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            answer = Answer.create_answer(
                content=serializer.validated_data['content'],
                author=request.user,
                question=question
            )
            
            answer_serializer = AnswerSerializer(answer, context={'request': request})
            return Response({
                "message": "留言發布成功",
                **answer_serializer.data
            }, status=status.HTTP_201_CREATED)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """刪除回答"""
        try:
            answer = self.get_object()
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

    @action(detail=True, methods=['post'])
    def like_answer(self, request, pk=None):
        try:
            answer = self.get_object()
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
