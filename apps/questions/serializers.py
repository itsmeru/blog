from rest_framework import serializers
from apps.questions.models import Question, QuestionLike
from core.app.base.serializer import SuccessSerializer


class QuestionSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "title",
            "content",
            "tags",
            "created_at",
            "author",
            "views",
            "likes",
            "answer_count",
            "is_liked",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "views",
            "likes",
            "answer_count",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return QuestionLike.objects.filter(user=request.user, question=obj).exists()
        return False


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["title", "content", "tags"]

    def validate_title(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("標題不能為空")
        return value.strip()

    def validate_content(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("內容不能為空")
        return value.strip()

    # 移除 create 方法，移到 service 層處理


# 成功回應序列化器
QuestionSuccessResponseSerializer = SuccessSerializer(
    QuestionSerializer(), "QuestionSuccessResponseSerializer"
)

QuestionListResponseSerializer = SuccessSerializer(
    QuestionSerializer(), "QuestionListResponseSerializer"
)
