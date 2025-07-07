from django.urls import path

from . import views

app_name = "questions"

urlpatterns = [
    path("", views.questions_handler, name="questions_handler"),
    path("<int:question_id>/", views.get_question_detail, name="get_question_detail"),
    path("<int:question_id>/answers/", views.answers_handler, name="answers_handler"),
    path("<int:question_id>/like/", views.like_question, name="like_question"),
    path("<int:question_id>/view/", views.view_question, name="view_question"),
    path("answers/<int:answer_id>/like/", views.like_answer, name="like_answer"),
]