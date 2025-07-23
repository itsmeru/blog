from django.urls import path
from .views import AnswerCreateView, AnswerDetailView, AnswerLikeView

app_name = "answers"

urlpatterns = [
    path('', AnswerCreateView.as_view(), name='answer_create'),
    path('<int:answer_id>/', AnswerDetailView.as_view(), name='answer_detail'),
    path('<int:answer_id>/like/', AnswerLikeView.as_view(), name='answer_like'),
]
