from django.db import models
from django.core.paginator import Paginator
from django.db.models import Q

from apps.users.models import User


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    answer_count = models.IntegerField(default=0)

    @classmethod
    def get_questions(cls, page, size, keyword, order_field, tags=None):
        queryset = cls.objects.all()

        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(content__icontains=keyword)
            )

        if order_field == "hot":
            queryset = queryset.order_by("-views")
        else:
            queryset = queryset.order_by("-created_at")

        paginator = Paginator(queryset, size)
        return paginator.get_page(page)

    @classmethod
    def create_question(cls, title, content, author, tags=None):
        return cls.objects.create(
            title=title, content=content, author=author, tags=tags
        )

    def increment_views(self):
        self.views += 1
        self.save()

    def toggle_like(self, user):
        like_record, created = QuestionLike.objects.get_or_create(
            user=user, question=self
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
        return QuestionLike.objects.filter(user=user, question=self).exists()

    def get_detail_data(self, user=None):
        answers = self.answers.all().order_by("created_at")
        answers_data = []

        for answer in answers:
            answer_is_liked = False
            if user:
                answer_is_liked = answer.is_liked_by_user(user)

            answers_data.append(
                {
                    "id": answer.id,
                    "content": answer.content,
                    "created_at": answer.created_at.strftime("%Y-%m-%d %H:%M"),
                    "author": answer.author.username if answer.author else "匿名",
                    "likes": answer.likes,
                    "is_liked": answer_is_liked,
                }
            )

        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "author": self.author.username if self.author else "匿名",
            "views": self.views,
            "likes": self.likes,
            "answer_count": self.answer_count,
            "is_liked": self.is_liked_by_user(user) if user else False,
            "answers": answers_data,
        }


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")
