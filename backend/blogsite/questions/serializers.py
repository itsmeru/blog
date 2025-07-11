from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from questions.models import Question, QuestionLike

class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'content', 'tags', 'created_at',
            'author', 'views', 'likes', 'answer_count', 'is_liked',
            'is_author'
        ]
    
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'account'):
            return QuestionLike.objects.filter(user=request.account, question=obj).exists()
        return False
    
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_author(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'account'):
            return obj.author == request.account
        return False

class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['title', 'content']
    
    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("標題至少需要5個字符")
        return value
    
    def validate_content(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("內容至少需要10個字符")
        return value

class QuestionListQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1, min_value=1)
    size = serializers.IntegerField(default=5, min_value=1, max_value=50)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    sort = serializers.ChoiceField(choices=['latest', 'hot'], default='latest')

class AnswerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')
    author = serializers.CharField()
    likes = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    
    def validate_content(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("回答內容不能為空")
        return value
    