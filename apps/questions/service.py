from apps.questions.repository import QuestionRepository
from apps.questions.serializers import QuestionCreateSerializer
from rest_framework.exceptions import NotFound, PermissionDenied


class QuestionService:
    repository_class = QuestionRepository

    @classmethod
    def create_question(cls, data, user):
        serializer = QuestionCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        question = cls.repository_class.create_question(
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            author=user,
            tags=serializer.validated_data.get("tags", ""),
        )
        return question

    @classmethod
    def list_questions(cls, page=1, size=10, keyword=None, tags=None):
        questions = cls.repository_class.get_questions_with_filters(
            page, size, keyword, tags or ""
        )
        return questions

    @classmethod
    def get_question(cls, question_id):
        question = cls.repository_class.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")
        return question

    @classmethod
    def update_question(cls, question_id, user, data, partial=False):
        question = cls.repository_class.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")
        if question.author != user:
            raise PermissionDenied("您沒有權限修改此問題")

        question = cls.repository_class.update_question(question, data, partial=partial)
        return question

    @classmethod
    def delete_question(cls, question_id, user):
        question = cls.repository_class.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")
        if question.author != user:
            raise PermissionDenied("您沒有權限刪除此問題")

        cls.repository_class.delete_question(question)
        return True

    @classmethod
    def toggle_like(cls, question_id, user):
        question = cls.repository_class.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")

        is_liked = cls.repository_class.toggle_like(question, user)
        return question, is_liked

    @classmethod
    def increment_views(cls, question_id):
        question = cls.repository_class.get_by_id(question_id)
        if not question:
            raise NotFound("問題不存在")

        cls.repository_class.increment_views(question)
        return question
