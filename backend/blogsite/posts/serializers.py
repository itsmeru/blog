from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Post


class PostListQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(min_value=1, default=1)
    size = serializers.IntegerField(min_value=1, max_value=50, default=3)
    keyword = serializers.CharField(max_length=100, required=False, allow_blank=True, default='')
    tags = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    order = serializers.ChoiceField(
        choices=['asc', 'desc'], 
        default='desc',
        help_text="排序方式：asc(升序) 或 desc(降序)"
    )


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'tags', 'image', 'author', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']
    
    @extend_schema_field(OpenApiTypes.STR)
    def get_image(self, obj):
        return obj.get_image_data_url()


class PostCreateSerializer(serializers.ModelSerializer):
    image = serializers.FileField(required=False, allow_null=True)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'tags', 'image']
    
    def validate_title(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("標題不能為空")
        return value.strip()
    
    def validate_content(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("內容不能為空")
        return value.strip()

    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("圖片大小不能超過5MB")
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("只支援 JPEG、PNG、GIF、WebP 格式的圖片")
        
        return value
    
    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        return Post.create_post_with_image(
            title=validated_data['title'],
            content=validated_data['content'],
            tags=validated_data.get('tags', ''),
            image_file=image_file,
            author=self.context['request'].account
        ) 