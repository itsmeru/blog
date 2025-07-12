import jwt

from django.conf import settings

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from accounts.serializers import (
    AccountCreateSerializer, 
    AccountSerializer,
    ForgotPasswordSerializer,
    ResetTokenSerializer,
    ResetPasswordSerializer,
    AccountUpdateSerializer,
    LoginSerializer,
    RefreshTokenSerializer
)
from accounts.utils import login_check

from .models import Account, PasswordResetToken
from posts.models import Post
from questions.models import Question, Answer

class AccountViewSet(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        action_to_serializer = {
            'register': AccountCreateSerializer,
            'login': LoginSerializer,
            'refresh_token': RefreshTokenSerializer,
            'forgot_password': ForgotPasswordSerializer,
            'verify_reset_token': ResetTokenSerializer,
            'reset_password': ResetPasswordSerializer,
            'change_password': AccountUpdateSerializer,
            'change_username': AccountUpdateSerializer,
        }
        
        return action_to_serializer.get(self.action, AccountSerializer)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        account = serializer.save()
        return Response({
            "message": "註冊成功",
            "username": account.username
        }, status=status.HTTP_201_CREATED)


    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        account = serializer.validated_data['account']
        access_token, refresh_token = account.generate_tokens()
        
        response = Response({
            "access_token": access_token,
            "username": account.username
        })
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            max_age=60 * 60 * 24 * 7
        )
        return response

    @action(detail=False, methods=['get'])
    def refresh_token(self, request):
        serializer = self.get_serializer(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        account = serializer.validated_data['account']
        access_token, new_refresh_token = account.generate_tokens()
        
        response = Response({
            "access_token": access_token,
            "username": account.username
        })
        response.set_cookie(
            "refresh_token", new_refresh_token, httponly=True, max_age=60 * 60 * 24 * 7
        )
        return response

    @action(detail=False, methods=['post'])
    def logout(self, request):
        response = Response({
            "message": "Logout successfully"
        })
        response.delete_cookie("refresh_token", path="/")
        return response

    @action(detail=False, methods=['post'])
    @login_check
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.account
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response({
                "message": "舊密碼錯誤"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            "message": "密碼更改成功，請重新登入",
            "require_relogin": True
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    @login_check
    def change_username(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_username = serializer.validated_data.get('new_username')
        
        if new_username:
            user = request.account
            user.username = new_username
            user.save()
            
            return Response({
                "message": "用戶名更改成功",
                "username": new_username
            }, status=status.HTTP_200_OK)
        

    @action(detail=False, methods=['get'])
    @login_check
    def profile_stats(self, request):
        user = request.account
        posts_count = Post.objects.filter(author=user).count()
        questions_count = Question.objects.filter(author=user).count()
        answers_count = Answer.objects.filter(author=user).count()
        
        return Response({
            "posts_count": posts_count,
            "questions_count": questions_count,
            "answers_count": answers_count,
            "total_content": posts_count + questions_count + answers_count
        }, status=status.HTTP_200_OK)



    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']        
        reset_token = PasswordResetToken.create_token(email)
        
        reset_token.send_reset_email()
        return Response({
            "message": f"驗證碼已發送到 {email}，請檢查您的郵箱"
        }, status=status.HTTP_200_OK)
       

    @action(detail=False, methods=['post'])
    def verify_reset_token(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response({
            "message": "驗證碼正確",
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "message": "密碼重設成功，請使用新密碼登入"
        }, status=status.HTTP_200_OK)
