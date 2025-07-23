from apps.answers.models import Answer, AnswerLike


class AnswerRepository:
    @staticmethod
    def get_by_id(answer_id):
        return Answer.objects.filter(id=answer_id).first()

    @staticmethod
    def get_by_question(question_id):
        return Answer.objects.filter(question_id=question_id).order_by("-created_at")

    @staticmethod
    def toggle_like(answer, user):
        like_record, created = AnswerLike.objects.get_or_create(
            user=user, answer=answer
        )
        if created:
            answer.likes += 1
            answer.save()
            return True
        else:
            like_record.delete()
            answer.likes = max(0, answer.likes - 1)
            answer.save()
            return False

    @staticmethod
    def is_liked_by_user(answer, user):
        return AnswerLike.objects.filter(user=user, answer=answer).exists()

    @staticmethod
    def get_liked_answer_ids_by_user(user, question_id):
        return AnswerLike.objects.filter(
            user=user, answer__question_id=question_id
        ).values_list("answer_id", flat=True)
