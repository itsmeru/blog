
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from accounts.utils import login_check
from posts.models import Post
from .serializers import PostSerializer, PostCreateSerializer, PostListQuerySerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [AllowAny]
    serializer_class = PostSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer

    def list(self, request):
        """獲取貼文列表"""
        # 驗證查詢參數
        query_serializer = PostListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({
                "message": "Invalid query parameters",
                "errors": query_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 獲取驗證後的參數
        validated_data = query_serializer.validated_data
        page = validated_data['page']
        size = validated_data['size']
        keyword = validated_data['keyword']
        tags = validated_data['tags']
        order_by = validated_data['order']
        order_field = "-created_at" if order_by == "desc" else "created_at"

        posts_page = Post.get_posts(page, size, keyword, order_field, tags)
        
        serializer = PostSerializer(posts_page, many=True) # True -> 列表, False -> 字典
        
        return Response({
            "posts": serializer.data,
            "total": posts_page.paginator.count,
            "num_pages": posts_page.paginator.num_pages,
            "current_page": posts_page.number,
        })

    @login_check
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
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