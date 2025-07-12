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
    VerifyResetTokenSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    ChangeUsernameSerializer
)
from accounts.utils import login_check

from .models import Account, PasswordResetToken
from posts.models import Post
from questions.models import Question, Answer

class AccountViewSet(viewsets.GenericViewSet):
    queryset = Account.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'register']:
            return AccountCreateSerializer
        elif self.action == 'forgot_password':
            return ForgotPasswordSerializer
        elif self.action == 'verify_reset_token':
            return VerifyResetTokenSerializer
        elif self.action == 'reset_password':
            return ResetPasswordSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'change_username':
            return ChangeUsernameSerializer
        return AccountSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            account = serializer.save()
            return Response({
                "message": "註冊成功",
                "username": account.username
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "註冊失敗",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({
                "message": "用戶名和密碼都是必填的"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response({
                "message": "用戶不存在"
            }, status=status.HTTP_404_NOT_FOUND)

        if not account.check_password(password):
            return Response({
                "message": "用戶名或密碼錯誤"
            }, status=status.HTTP_401_UNAUTHORIZED)

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
        refresh_token = request.COOKIES.get("refresh_token")
        
        if not refresh_token:
            return Response({
                "error": "No refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])            
            user_id = payload.get("user_id")            
            account = Account.objects.get(id=user_id)
            
            access_token, new_refresh_token = account.generate_tokens()
            response = Response({
                "access_token": access_token,
                "username": account.username
            })
            response.set_cookie(
                "refresh_token", new_refresh_token, httponly=True, max_age=60 * 60 * 24 * 7
            )
            return response
        except Account.DoesNotExist:
            return Response({
                "error": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except (
            jwt.ExpiredSignatureError,
            jwt.InvalidTokenError,
            jwt.DecodeError,
            jwt.InvalidSignatureError,
        ) as e:
            return Response({
                "success": False,
                "error": "Invalid or expired token"
            }, status=status.HTTP_401_UNAUTHORIZED)

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
        
        new_username = serializer.validated_data['new_username']
        
        if Account.objects.filter(username=new_username).exclude(id=request.account.id).exists():
            return Response({
                "message": "該用戶名已被使用"
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
        account = Account.objects.get(email=email)
        
        # 創建重設密碼驗證碼並發送郵件
        reset_token = PasswordResetToken.create_token(email)
        
        if reset_token.send_reset_email():
            return Response({
                "message": f"驗證碼已發送到 {email}，請檢查您的郵箱"
            }, status=status.HTTP_200_OK)
        else:
            reset_token.delete()
            return Response({
                "message": "郵件發送失敗，請稍後再試"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_reset_token(self, request):
        """驗證重設密碼驗證碼"""
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
