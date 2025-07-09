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
            OpenApiParameter(name='order', type=str, default='desc', enum=['asc', 'desc'], description='排序方式'),
        ]
    )
    def list(self, request):
        """取得問題列表"""
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
        order_by = validated_data['order']
        order_field = "-created_at" if order_by == "desc" else "created_at"

        questions_page = Question.get_questions(page, size, keyword, order_field)
        serializer = QuestionSerializer(questions_page, many=True, context={'request': request})
        
        return Response({
            "questions": serializer.data,
            "total": questions_page.paginator.count,
            "num_pages": questions_page.paginator.num_pages,
            "current_page": questions_page.number,
        })

    @login_check
    def create(self, request):
        """創建新問題"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            question = Question.create_question(
                title=serializer.validated_data['title'],
                content=serializer.validated_data['content'],
                author=request.account
            )
            return Response({
                "message": "Question created successfully",
                "question_id": question.id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Validation error",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(exclude=True)
    def retrieve(self, request, *args, **kwargs):
        """隱藏此端點"""
        pass

    @action(detail=True, methods=['get', 'post'])
    @login_check
    def answers(self, request, pk=None):
        """取得問題詳情和回答，或新增回答"""
        try:
            question = self.get_object()
            # 自動增加瀏覽數
            question.increment_views()
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if request.method == 'GET':
            # 使用模型的業務邏輯獲取詳情數據
            data = question.get_detail_data(user=request.account)
            return Response(data)
        
        elif request.method == 'POST':
            try:
                data = json.loads(request.body)
                content = data.get("content")
                
                if not content or len(content.strip()) < 5:
                    return Response({"message": "回答內容至少需要5個字符"}, status=status.HTTP_400_BAD_REQUEST)
                
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
                    "is_liked": False,  # 新創建的回答默認未按讚
                }
                
                # 使用序列化器進行輸出驗證
                serializer = AnswerSerializer(response_data)
                return Response(serializer.data)
            except json.JSONDecodeError:
                return Response({"message": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": f"創建回答失敗: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    @login_check
    def like(self, request, pk=None):
        """按讚/收回讚問題"""
        try:
            question = self.get_object()
            is_liked, message = question.toggle_like(request.account)
            
            # 使用序列化器進行輸出驗證
            serializer = QuestionSerializer(question, context={'request': request})
            return Response({
                "question": serializer.data,
                "is_liked": is_liked,
                "message": message
            })
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"按讚失敗: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """增加問題瀏覽數"""
        try:
            question = self.get_object()
            question.increment_views()
            
            # 使用序列化器進行輸出驗證
            serializer = QuestionSerializer(question, context={'request': request})
            return Response({
                "question": serializer.data,
                "message": "瀏覽記錄成功"
            })
        except Question.DoesNotExist:
            return Response({"message": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"瀏覽記錄失敗: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    @login_check
    def like_answer(self, request):
        """按讚/收回讚回答"""
        try:
            answer_id = request.data.get('answer_id')
            answer = Answer.objects.get(id=answer_id)
            is_liked, message = answer.toggle_like(request.account)
            
            # 使用序列化器進行輸出驗證
            answer_data = {
                "id": answer.id,
                "content": answer.content,
                "created_at": answer.created_at,  # 傳入 datetime 對象
                "author": answer.author.username if answer.author else "匿名",
                "likes": answer.likes,
                "is_liked": is_liked,
            }
            
            serializer = AnswerSerializer(answer_data)
            return Response({
                "answer": serializer.data,
                "is_liked": is_liked,
                "message": message
            })
        except Answer.DoesNotExist:
            return Response({"message": "Answer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"按讚失敗: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
