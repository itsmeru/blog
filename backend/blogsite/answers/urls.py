from rest_framework.routers import DefaultRouter
from . import views

app_name = 'answers'

router = DefaultRouter()
router.register(r'', views.AnswerViewSet, basename='answer')

urlpatterns = router.urls 