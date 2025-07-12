from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
import json

from accounts.utils import login_check
from questions.models import Question, Answer
from questions.serializers import (
    QuestionSerializer, QuestionCreateSerializer, QuestionListQuerySerializer,
    AnswerSerializer
)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return QuestionCreateSerializer
        return QuestionSerializer

    @extend_schema(
        summary="取得問題列表",
        description="取得分頁的問題列表，支援搜尋",
        parameters=[
            OpenApiParameter(name='page', type=int, default=1, required=True, description='頁碼'),
            OpenApiParameter(name='size', type=int, default=5, required=True, description='每頁數量'),
            OpenApiParameter(name='keyword', type=str, description='搜尋關鍵字'),
            OpenApiParameter(name='order_fielde', type=str, default='latest', enum=['hot', 'latest'], description='排序方式'),
        ]
    )
    def list(self, request):
        query_serializer = QuestionListQuerySerializer(data=request.query_params)
        if not query_serializer.is_valid():
            return Response({
                "message": "Invalid query parameters",
                "errors": query_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = query_serializer.validated_data
        page = validated_data['page']
        size = validated_data['size']
        keyword = validated_data['keyword']
        sort = validated_data['sort']

        questions_page = Question.get_questions(page, size, keyword, sort)
        serializer = QuestionSerializer(questions_page, many=True, context={'request': request})
        
        return Response({
            "questions": serializer.data,
            "total": questions_page.paginator.count,
            "num_pages": questions_page.paginator.num_pages,
            "current_page": questions_page.number,
        })

    @login_check
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            tags = request.data.get('tags', '')
            question = Question.create_question(
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                author=request.account,
                tags=tags
            )
            return Response({
                "message": "Question created successfully",
                "question_id": question.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors,
                "received_data": request.data
            }, status=status.HTTP_400_BAD_REQUEST)

    @login_check
    def destroy(self, request, pk=None):
        try:
            question: Question = self.get_object()
            
            if question.author != request.account:
                return Response({
                    "message": "您沒有權限刪除此問題"
                }, status=status.HTTP_403_FORBIDDEN)
            
            question.delete()
            
            return Response({"message": "Question deleted successfully"})
            
        except Question.DoesNotExist:
            return Response({
                "message": "Question not found"
            }, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="取得問題詳情",
        description="根據ID取得特定問題的詳細資訊"
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            question = self.get_object()
            question.increment_views()
            
            user = None
            if hasattr(request, 'account'):
                user = request.account
                
            data = question.get_detail_data(user=user)
            return Response(data)
        except Question.DoesNotExist:
            return Response({
                "message": "Question not found"
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get', 'post'])
    def answers(self, request, pk=None):
        try:
            question: Question = self.get_object()
            question.increment_views()
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            user = None
            if hasattr(request, 'account'):
                user = request.account
            data = question.get_detail_data(user=user)
            return Response(data)
        
        elif request.method == 'POST':
            auth_header = request.META.get("HTTP_AUTHORIZATION")
            if not auth_header or not auth_header.startswith("Bearer "):
                return Response({
                    "message": "請先登入後再發表留言"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(" ")[1]
            try:
                import jwt
                from accounts.models import Account
                from django.conf import settings
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                account = Account.objects.get(id=user_id)
                request.account = account
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Account.DoesNotExist):
                return Response({
                    "message": "登入已過期，請重新登入"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                data = json.loads(request.body)
                content = data.get("content")
                
                if not content:
                    return Response({"message": "回答內容不能為空"}, status=status.HTTP_400_BAD_REQUEST)
                
                answer = Answer.create_answer(
                    content=content,
                    author=request.account,
                    question=question
                )
                
                response_data = {
                    "id": answer.id,
                    "content": answer.content,
                    "created_at": answer.created_at,
                    "author": answer.author.username,
                    "likes": answer.likes,
                    "is_liked": False,
                }
                
                serializer = AnswerSerializer(response_data)
                return Response(serializer.data)
            except json.JSONDecodeError:
                return Response({"message": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @login_check
    def like(self, request, pk=None):
        try:
            question: Question = self.get_object()
            is_liked= question.toggle_like(request.account)
            
            serializer = QuestionSerializer(question, context={'request': request})
            return Response({
                "question": serializer.data,
                "is_liked": is_liked,
            })
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        try:
            question: Question = self.get_object()
            question.increment_views()
            
            serializer = QuestionSerializer(question, context={'request': request})
            return Response({
                "question": serializer.data,
                "message": "瀏覽記錄成功"
            })
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    @login_check
    def like_answer(self, request):
        try:
            answer_id = request.data.get('answer_id')
            answer = Answer.objects.get(id=answer_id)
            is_liked= answer.toggle_like(request.account)
            
            answer_data = {
                "id": answer.id,
                "content": answer.content,
                "created_at": answer.created_at,
                "author": answer.author.username if answer.author else "匿名",
                "likes": answer.likes,
                "is_liked": is_liked,
            }
            
            serializer = AnswerSerializer(answer_data)
            return Response({
                "answer": serializer.data,
                "is_liked": is_liked,
            })
        except Answer.DoesNotExist:
            return Response({"message": "Answer not found"}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['post'])
    @login_check
    def delete_answer(self, request):
        try:
            answer_id = request.data.get('answer_id')
            answer = Answer.objects.get(id=answer_id)
            
            if answer.author != request.account:
                return Response({
                    "message": "您沒有權限刪除此回答"
                }, status=status.HTTP_403_FORBIDDEN)
            
            answer.delete()
            
            return Response({
                "message": "回答刪除成功"
            }, status=status.HTTP_200_OK)
            
        except Answer.DoesNotExist:
            return Response({
                "message": "Answer not found"
            }, status=status.HTTP_404_NOT_FOUND)