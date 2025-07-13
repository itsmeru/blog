from rest_framework.routers import DefaultRouter
from . import views

app_name = 'questions'

router = DefaultRouter()
router.register(r'', views.QuestionViewSet, basename='question')


urlpatterns = router.urls