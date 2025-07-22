from django.urls import path
from .views import AnswerCreateView, AnswerDetailView, AnswerLikeView

urlpatterns = [
    path('', AnswerCreateView.as_view(), name='answer_create'),
    path('<int:answer_id>/', AnswerDetailView.as_view(), name='answer_detail'),
    path('<int:pk>/like/', AnswerLikeView.as_view(), name='answer_like'),
]
