from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q

from accounts.models import Account

class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)
    
    @classmethod
    def get_questions(cls, page, size, keyword, order_field, tags=None):
        """獲取分頁的問題列表"""
        queryset = cls.objects.all()
        
        # 搜尋關鍵字
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )
        
        # 排序
        queryset = queryset.order_by(order_field)
        
        # 分頁
        paginator = Paginator(queryset, size)
        return paginator.get_page(page)
    
    @classmethod
    def create_question(cls, title, content, author):
        """創建新問題"""
        return cls.objects.create(
            title=title,
            content=content,
            author=author
        )
    
    def increment_views(self):
        """增加瀏覽數"""
        self.views += 1
        self.save()
    
    def toggle_like(self, user):
        """切換按讚狀態"""
        like_record, created = QuestionLike.objects.get_or_create(
            user=user,
            question=self
        )
        
        if created:
            # 新按讚
            self.likes += 1
            self.save()
            return True, "按讚成功"
        else:
            # 收回讚
            like_record.delete()
            self.likes = max(0, self.likes - 1)
            self.save()
            return False, "收回讚成功"
    
    def is_liked_by_user(self, user):
        """檢查用戶是否已按讚"""
        return QuestionLike.objects.filter(user=user, question=self).exists()
    
    def get_detail_data(self, user=None):
        """獲取問題詳情數據"""
        answers = self.answers.all().order_by('created_at')
        answers_data = []
        
        for answer in answers:
            answer_is_liked = False
            if user:
                answer_is_liked = answer.is_liked_by_user(user)
            
            answers_data.append({
                "id": answer.id,
                "content": answer.content,
                "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M"),
                "author": answer.author.username if answer.author else "匿名",
                "likes": answer.likes,
                "is_liked": answer_is_liked,
            })
        
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "author": self.author.username if self.author else "匿名",
            "views": self.views,
            "likes": self.likes,
            "answer_count": self.answer_count,
            "is_liked": self.is_liked_by_user(user) if user else False,
            "answers": answers_data,
        }
    

class Answer(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    likes = models.IntegerField(default=0)
    
    @classmethod
    def create_answer(cls, content, author, question):
        """創建新回答"""
        answer = cls.objects.create(
            content=content,
            author=author,
            question=question
        )
        
        # 更新問題的回答數
        question.answer_count = question.answers.count()
        question.save()
        
        return answer
    
    def toggle_like(self, user):
        """切換按讚狀態"""
        like_record, created = AnswerLike.objects.get_or_create(
            user=user,
            answer=self
        )
        
        if created:
            # 新按讚
            self.likes += 1
            self.save()
            return True, "按讚成功"
        else:
            # 收回讚
            like_record.delete()
            self.likes = max(0, self.likes - 1)
            self.save()
            return False, "收回讚成功"
    
    def is_liked_by_user(self, user):
        """檢查用戶是否已按讚"""
        return AnswerLike.objects.filter(user=user, answer=self).exists()
    

class QuestionLike(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'question')


class AnswerLike(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'answer')
    