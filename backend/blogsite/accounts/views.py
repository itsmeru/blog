import jwt
from datetime import datetime, timedelta

from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from accounts.serializers import AccountCreateSerializer, AccountSerializer

from .models import Account

class AccountViewSet(viewsets.ViewSet):
    queryset = Account.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action in ['create', 'register']:
            return AccountCreateSerializer
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

        access_token, refresh_token = self.generate_token(account)
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
            
            access_token, new_refresh_token = self.generate_token(account)
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

    def generate_token(self, account):
        access_payload = {
            "user_id": account.id,
            "username": account.username,
            "exp": datetime.utcnow() + timedelta(minutes=30),
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm="HS256")

        refresh_payload = {
            "user_id": account.id,
            "exp": datetime.utcnow() + timedelta(days=7),
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm="HS256")

        return access_token, refresh_token
