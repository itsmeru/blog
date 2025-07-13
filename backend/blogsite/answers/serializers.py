from rest_framework import serializers
from questions.models import Question

from answers.models import Answer, AnswerLike

class AnswerSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Answer
        fields = ['id', 'content', 'created_at', 'author', 'likes', 'is_liked']
        read_only_fields = ['id', 'author', 'created_at', 'likes']
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return AnswerLike.objects.filter(user=request.user, answer=obj).exists()
        return False


class AnswerCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Answer
        fields = ['content', 'question_id']
    
    def validate_content(self, value):
        if not value or len(value.strip()) < 1:
            raise serializers.ValidationError("內容不能為空")
        return value.strip()
    
    def validate_question_id(self, value):
        try:
            Question.objects.get(id=value)
        except Question.DoesNotExist:
            raise serializers.ValidationError("問題不存在")
        return value
    
    def create(self, validated_data):
        question_id = validated_data.pop('question_id')
        question = Question.objects.get(id=question_id)
        
        answer = Answer.objects.create(
            content=validated_data['content'],
            author=self.context['request'].user,
            question=question
        )
        
        question.answer_count = question.answers.count()
        question.save()
        
        return answer 