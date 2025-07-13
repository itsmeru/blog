from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter

from questions.models import Question
from questions.serializers import (
    QuestionSerializer,
    QuestionCreateSerializer,
    QuestionListQuerySerializer,
)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'view_question']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        return QuestionSerializer

    @extend_schema(
        summary="取得問題列表",
        description="取得分頁的問題列表，支援搜尋",
        parameters=[
            OpenApiParameter(name='page', type=int, default=1, required=True, description='頁碼'),
            OpenApiParameter(name='size', type=int, default=5, required=True, description='每頁數量'),
            OpenApiParameter(name='keyword', type=str, description='搜尋關鍵字'),
            OpenApiParameter(name='order_fielde', type=str, default='latest', enum=['hot', 'latest'], description='排序方式'),
        ]
    )
    def list(self, request):
        query_serializer = QuestionListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({
                "message": "Invalid query parameters",
                "errors": query_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = query_serializer.validated_data
        page = validated_data['page']
        size = validated_data['size']
        keyword = validated_data['keyword']
        sort = validated_data['sort']

        questions_page = Question.get_questions(page, size, keyword, sort)
        serializer = QuestionSerializer(questions_page, many=True, context={'request': request})
        
        return Response({
            "questions": serializer.data,
            "total": questions_page.paginator.count,
            "num_pages": questions_page.paginator.num_pages,
            "current_page": questions_page.number,
        })

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        question = serializer.save()
        
        return Response({
            "message": "問題發布成功",
            "question_id": question.id
        }, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        try:
            question = self.get_object()
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

    @action(detail=True, methods=['post'])
    def like_question(self, request, pk=None):
        try:
            question = self.get_object()
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

    @action(detail=True, methods=['post'])
    def view_question(self, request, pk=None):
        try:
            question = self.get_object()
            question.increment_views()
            return Response({
                "message": "瀏覽次數更新成功",
                "views": question.views
            }, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({
                "message": "問題不存在"
            }, status=status.HTTP_404_NOT_FOUND)