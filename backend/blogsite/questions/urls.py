from django.urls import path
from .views import (
    QuestionCreateView, QuestionDetailView, QuestionDeleteView,
    QuestionLikeView, QuestionViewView
)

app_name = 'questions'

urlpatterns = [
    path('', QuestionCreateView.as_view(), name='question_create'),  # POST /api/questions/
    path('<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),  # GET /api/questions/<question_id>/
    path('delete/<int:question_id>/', QuestionDeleteView.as_view(), name='question_delete'),  # DELETE /api/questions/delete/<question_id>/
    path('<int:question_id>/like/', QuestionLikeView.as_view(), name='question_like'),  # POST /api/questions/<question_id>/like/
    path('<int:question_id>/view/', QuestionViewView.as_view(), name='question_view'),  # POST /api/questions/<question_id>/view/
]