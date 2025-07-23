from rest_framework import serializers
from .models import Post
from core.app.base.serializer import SuccessSerializer


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "title", "content", "tags", "image", "author", "created_at"]
        read_only_fields = ["id", "author", "created_at"]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            url = obj.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, allow_null=False)
    content = serializers.CharField(required=True, allow_null=False)
    tags = serializers.CharField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ["title", "content", "tags", "image"]

    def validate_title(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("標題不能為空")
        return value.strip()

    def validate_content(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("內容不能為空")
        return value.strip()


class PostUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_null=True)
    content = serializers.CharField(required=False, allow_null=True)
    tags = serializers.CharField(required=False, allow_null=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Post
        fields = ["title", "content", "tags", "image"]


PostSuccessResponseSerializer = SuccessSerializer(
    PostSerializer(), "PostSuccessResponseSerializer"
)

PostListResponseSerializer = SuccessSerializer(
    PostSerializer(), "PostListResponseSerializer"
)
