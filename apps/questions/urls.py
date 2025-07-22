from django.urls import path
from .views import QuestionListCreateView, QuestionDetailView
from apps.answers.views import AnswerListView

app_name = 'questions'

urlpatterns = [
    path('', QuestionListCreateView.as_view(), name='question_create_list'),
    path('<int:question_id>/', QuestionDetailView.as_view(), name='question_detail'),
    path('<int:question_id>/answers/', AnswerListView.as_view(), name='answer_list'),
]