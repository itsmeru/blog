from apps.answers.repository import AnswerRepository
from apps.answers.serializers import AnswerCreateSerializer
from apps.questions.models import Question
from rest_framework.exceptions import NotFound, PermissionDenied
from apps.answers.models import Answer


class AnswerService:
    repository_class = AnswerRepository

    @classmethod
    def create_answer(cls, data, user):
        serializer = AnswerCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.validated_data["question_id"]
        question = Question.objects.get(id=question_id)
        answer = Answer.objects.create(
            content=serializer.validated_data["content"], author=user, question=question
        )
        question.answer_count = question.answers.count()
        question.save()
        return answer

    @classmethod
    def list_answers(cls, question_id, user=None):
        question = Question.objects.filter(id=question_id).first()
        if not question:
            raise NotFound("問題不存在")
        answers = cls.repository_class.get_by_question(question_id)

        is_liked_map = {}
        if user and user.is_authenticated:
            liked_ids = set(
                cls.repository_class.get_liked_answer_ids_by_user(user, question_id)
            )
            for answer in answers:
                is_liked_map[answer.id] = answer.id in liked_ids
        else:
            for answer in answers:
                is_liked_map[answer.id] = False
        return answers, is_liked_map

    @classmethod
    def update_answer(cls, answer_id, user, data, partial=False):
        answer = cls.repository_class.get_by_id(answer_id)
        if not answer:
            raise NotFound("回答不存在")
        if answer.author != user:
            raise PermissionDenied("您沒有權限修改此回答")
        serializer = AnswerCreateSerializer(answer, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return answer

    @classmethod
    def delete_answer(cls, answer_id, user):
        answer = cls.repository_class.get_by_id(answer_id)
        if not answer:
            raise NotFound("回答不存在")
        if answer.author != user:
            raise PermissionDenied("您沒有權限刪除此回答")
        answer.delete()
        return True

    @classmethod
    def toggle_like(cls, answer_id, user):
        answer = cls.repository_class.get_by_id(answer_id)
        if not answer:
            raise NotFound("回答不存在")
        is_liked = cls.repository_class.toggle_like(answer, user)
        return answer, is_liked
