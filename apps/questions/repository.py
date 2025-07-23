from apps.questions.models import Question, QuestionLike
from django.core.paginator import Paginator


class QuestionRepository:
    @staticmethod
    def get_by_id(question_id):
        return Question.objects.filter(id=question_id).first()

    @staticmethod
    def toggle_like(question, user):
        like_record, created = QuestionLike.objects.get_or_create(
            user=user, question=question
        )
        if created:
            question.likes += 1
            question.save()
            return True
        else:
            like_record.delete()
            question.likes = max(0, question.likes - 1)
            question.save()
            return False

    @staticmethod
    def is_liked_by_user(question, user):
        return QuestionLike.objects.filter(user=user, question=question).exists()

    @staticmethod
    def increment_views(question):
        question.views += 1
        question.save()

    @staticmethod
    def get_questions_with_filters(page=1, size=10, keyword=None, tags=None):
        qs = Question.objects.all()
        if keyword:
            qs = qs.filter(title__icontains=keyword)
        if tags:
            qs = qs.filter(tags__icontains=tags)
        paginator = Paginator(qs, size)
        return paginator.get_page(page)

    @staticmethod
    def update_question(question, data, partial=False):
        for field, value in data.items():
            if hasattr(question, field):
                setattr(question, field, value)
        question.save()
        return question
    
    @staticmethod
    def delete_question(question):
        question.delete()
        return True