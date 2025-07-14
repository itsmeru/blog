from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from posts.models import Post
from .serializers import PostSerializer, PostCreateSerializer
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter


class PostPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'size'
    max_page_size = 50

class PostViewSet(viewsets.ModelViewSet):
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = PostPagination
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all()
        keyword = self.request.query_params.get('keyword', '').strip()
        tags = self.request.query_params.get('tags', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(name='keyword', type=str, description='Keyword search (fuzzy match in title or content)'),
            OpenApiParameter(name='tags', type=str, description='Tag search (comma separated)'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            post = serializer.save()
        
            return Response({
                "message": "貼文建立成功",
                "post_id": post.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "驗證錯誤",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        try:
            post = self.get_object()
            
            if post.author != request.user:
                return Response({
                    "message": "您沒有權限刪除此貼文"
                }, status=status.HTTP_403_FORBIDDEN)
            
            post.delete()
            
            return Response({
                "message": "貼文刪除成功"
            }, status=status.HTTP_200_OK)
            
        except Post.DoesNotExist:
            return Response({
                "message": "貼文不存在"
            }, status=status.HTTP_404_NOT_FOUND)
    