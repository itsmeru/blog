from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter


from questions.models import Question
from questions.serializers import (
    QuestionSerializer,
    QuestionCreateSerializer,
)


class QuestionPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 50

class QuestionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Question.objects.all()
        keyword = self.request.query_params.get('keyword', '').strip()
        sort = self.request.query_params.get('sort', 'latest')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        if sort == 'hot':
            queryset = queryset.order_by('-views', '-likes')
        else:
            queryset = queryset.order_by('-created_at')
        return queryset

    pagination_class = QuestionPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'view_question']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        return QuestionSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='keyword', type=str, description='Keyword search (fuzzy match in title or content)'),
            OpenApiParameter(name='sort', type=str, enum=['hot', 'latest'], description='Sort by (hot: most popular, latest: newest, default)'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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