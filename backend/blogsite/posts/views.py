from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from posts.models import Post
from .serializers import PostSerializer, PostCreateSerializer, PostListQuerySerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='page', type=int, default=1, required=True, description='頁碼'),
            OpenApiParameter(name='size', type=int, default=3, required=True, description='每頁數量'),
            OpenApiParameter(name='keyword', type=str, description='搜尋關鍵字'),
            OpenApiParameter(name='tags', type=str, description='標籤篩選（逗號分隔）'),
            OpenApiParameter(name='order', type=str, default='desc', enum=['asc', 'desc'], description='排序方式'),
        ]
    )
    def list(self, request):
        query_serializer = PostListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({
                "message": "Invalid query parameters",
                "errors": query_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = query_serializer.validated_data
        page = validated_data['page']
        size = validated_data['size']
        keyword = validated_data['keyword']
        tags = validated_data['tags']

        posts_page = Post.get_posts(page, size, keyword, tags)
        
        serializer = PostSerializer(posts_page, many=True)
        
        return Response({
            "posts": serializer.data,
            "total": posts_page.paginator.count,
            "num_pages": posts_page.paginator.num_pages,
            "current_page": posts_page.number,
        })

    def create(self, request):
        serializer = PostCreateSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            post = serializer.save()
        
            return Response({
                "message": "Post created successfully",
                "post_id": post.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation error",
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
                "message": "Post not found"
            }, status=status.HTTP_404_NOT_FOUND)
    