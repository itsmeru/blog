from django.db import models
from apps.users.models import User
from apps.questions.models import Question


class Answer(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    likes = models.IntegerField(default=0)


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "answer")
