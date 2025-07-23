from django.urls import path
from .views import QuestionListView, QuestionDetailView, QuestionLikeView
from apps.answers.views import AnswerListView

app_name = 'questions'

urlpatterns = [
    path('', QuestionListView.as_view(), name='question_list'),  
    path('<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),
    path('<int:question_id>/answers/', AnswerListView.as_view(), name='answer_list'),
    path('<int:question_id>/like/', QuestionLikeView.as_view(), name='question_like'),
]
