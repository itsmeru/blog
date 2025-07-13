from rest_framework import serializers
from questions.models import Question, QuestionLike

class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = ['id', 'title', 'content', 'tags', 'created_at', 'author', 'views', 'likes', 'answer_count', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'views', 'likes', 'answer_count']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return QuestionLike.objects.filter(user=request.user, question=obj).exists()
        return False


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['title', 'content', 'tags']
    
    def validate_title(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("標題不能為空")
        return value.strip()
    
    def validate_content(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("內容不能為空")
        return value.strip()


class QuestionListQuerySerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1, min_value=1)
    size = serializers.IntegerField(default=5, min_value=1, max_value=50)
    keyword = serializers.CharField(required=False, allow_blank=True, default='')
    sort = serializers.ChoiceField(choices=['latest', 'hot'], default='latest')



    