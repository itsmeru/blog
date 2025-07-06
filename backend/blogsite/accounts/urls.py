from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('logout/', views.logout, name='logout'),
]