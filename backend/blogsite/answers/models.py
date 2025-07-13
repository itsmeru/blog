from django.db import models
from accounts.models import Account
from questions.models import Question

class Answer(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    likes = models.IntegerField(default=0)
    

    
    def toggle_like(self, user):
        like_record, created = AnswerLike.objects.get_or_create(
            user=user,
            answer=self
        )
        
        if created:
            self.likes += 1
            self.save()
            return True
        else:
            like_record.delete()
            self.likes = max(0, self.likes - 1)
            self.save()
            return False
    
    def is_liked_by_user(self, user):
        return AnswerLike.objects.filter(user=user, answer=self).exists()


class AnswerLike(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'answer')
