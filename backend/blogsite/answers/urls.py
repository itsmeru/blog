from django.urls import path
from .views import AnswerListView, AnswerLikeView, AnswerCreateView, AnswerDeleteView

app_name = 'answers'

urlpatterns = [
    path('', AnswerCreateView.as_view(), name='answer_list_create'),
    path('<int:question_id>/', AnswerListView.as_view(), name='answer_detail'),
    path('<int:answer_id>', AnswerDeleteView.as_view(), name='answer_delete'),
    path('<int:pk>/like/', AnswerLikeView.as_view(), name='answer_like'),
]
