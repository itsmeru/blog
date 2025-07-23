from apps.questions.repository import QuestionRepository
from apps.questions.serializers import QuestionCreateSerializer
from rest_framework.exceptions import NotFound, PermissionDenied


class QuestionService:
    @staticmethod
    def create_question(data, user):
        serializer = QuestionCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        question = QuestionRepository.create_question(
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            author=user,
            tags=serializer.validated_data.get("tags", ""),
        )
        return question

    @staticmethod
    def list_questions(page=1, size=10, keyword=None, tags=None):
        questions = QuestionRepository.get_questions_with_filters(
            page, size, keyword, tags or ""
        )
        return questions

    @staticmethod
    def get_question(question_id):
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")
        return question

    @staticmethod
    def update_question(question_id, user, data, partial=False):
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")
        if question.author != user:
            raise PermissionDenied("您沒有權限修改此問題")

        question = QuestionRepository.update_question(question, data, partial=partial)
        return question

    @staticmethod
    def delete_question(question_id, user):
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")
        if question.author != user:
            raise PermissionDenied("您沒有權限刪除此問題")

        QuestionRepository.delete_question(question)
        return True

    @staticmethod
    def toggle_like(question_id, user):
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")

        is_liked = QuestionRepository.toggle_like(question, user)
        return question, is_liked

    @staticmethod
    def increment_views(question_id):
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")

        QuestionRepository.increment_views(question)
        return question
