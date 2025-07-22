from django.urls import path
from .views import AnswerListView, AnswerDetailView, AnswerLikeView

app_name = "answers"

urlpatterns = [
    path('', AnswerListView.as_view(), name='answer_list'),
    path('<int:answer_id>/', AnswerDetailView.as_view(), name='answer_detail'),
    path('<int:pk>/like/', AnswerLikeView.as_view(), name='answer_like'),
]
