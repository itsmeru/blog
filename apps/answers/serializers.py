from rest_framework import serializers
from apps.answers.models import Answer
from core.app.base.serializer import SuccessSerializer

class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(
        format='%Y-%m-%d %H:%M', read_only=True
    )
    class Meta:
        model = Answer
        fields = ['id', 'content', 'created_at', 'author', 'likes']
        read_only_fields = ['id', 'author', 'created_at', 'likes']

AnswerSuccessResponseSerializer = SuccessSerializer(
    AnswerSerializer(), "AnswerSuccessResponseSerializer")

class AnswerCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Answer
        fields = ['content', 'question_id']

class AnswerListItemSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    is_liked = serializers.BooleanField()
    class Meta:
        model = Answer
        fields = ['id', 'content', 'created_at', 'author', 'likes', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'likes', 'is_liked']

AnswerListResponseSerializer = SuccessSerializer(
    AnswerListItemSerializer(), "AnswerListResponseSerializer"
)

class AnswerLikeDataSerializer(serializers.Serializer):
    is_liked = serializers.BooleanField()
    likes = serializers.IntegerField()

AnswerLikeSuccessResponseSerializer = SuccessSerializer(
    AnswerLikeDataSerializer(), "AnswerLikeSuccessResponseSerializer"
)
