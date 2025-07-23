from apps.questions.models import Question, QuestionLike

class QuestionRepository:
    @staticmethod
    def get_by_id(question_id):
        return Question.objects.filter(id=question_id).first()
    
    @staticmethod
    def toggle_like(question, user):
        like_record, created = QuestionLike.objects.get_or_create(
            user=user,
            question=question
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