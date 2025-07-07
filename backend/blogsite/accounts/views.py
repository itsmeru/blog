import json
from datetime import datetime, timedelta
import os

import jwt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from dotenv import load_dotenv

from .models import Account

load_dotenv()
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        # 解析 JSON 數據
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # 驗證必填欄位
        if not all([username, email, password]):
            return JsonResponse(
                {"success": False, "message": f"所有欄位都是必填的。"}, status=400
            )

        # 檢查用戶名是否已存在
        if Account.objects.filter(username=username).exists():
            return JsonResponse(
                {"success": False, "message": "用戶名已存在"}, status=400
            )

        # 檢查郵箱是否已存在
        if Account.objects.filter(email=email).exists():
            return JsonResponse(
                {"success": False, "message": "郵箱已被註冊"}, status=400
            )

        # 創建新用戶
        account = Account.objects.create(username=username, email=email)
        # 使用自定義的密碼加密方法
        account.set_password(password)
        account.save()

        return JsonResponse(
            {
                "success": True,
                "message": "註冊成功",
            }
        )

    except json.JSONDecodeError as e:
        return JsonResponse(
            {"success": False, "message": f"無效的 JSON 格式: {str(e)}"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"註冊失敗: {str(e)}"}, status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        # 解析 JSON 數據
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        # 驗證必填欄位
        if not email or not password:
            return JsonResponse(
                {"success": False, "message": "用戶名和密碼都是必填的"}, status=400
            )

        # 查找用戶
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return JsonResponse(
                {"success": False, "message": "用戶名或密碼錯誤"}, status=401
            )

        # 驗證密碼
        if not account.check_password(password):
            return JsonResponse(
                {"success": False, "message": "用戶名或密碼錯誤"}, status=401
            )

        access_token, refresh_token = generate_token(account)
        respnse = JsonResponse({"access_token": access_token})
        respnse.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            # secure=settings.DEBUG,
            max_age=60 * 60 * 24 * 7,
        )
        return respnse

    except json.JSONDecodeError:
        return JsonResponse(
            {"success": False, "message": "無效的 JSON 格式"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"登入失敗: {str(e)}"}, status=500
        )


def generate_token(account):
    access_payload = {
        "user_id": account.id,
        "username": account.username,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    access_token = jwt.encode(access_payload, os.getenv("SECRET_KEY"), algorithm="HS256")

    refresh_payload = {
        "user_id": account.id,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    refresh_token = jwt.encode(refresh_payload, os.getenv("SECRET_KEY"), algorithm="HS256")

    return access_token, refresh_token


@csrf_exempt
@require_http_methods(["GET"])
def refresh_token(request):
    refresh_token = request.COOKIES.get("refresh_token")
    if not refresh_token:
        return JsonResponse({"error": "No refresh token"}, status=401)
    try:
        payload = jwt.decode(refresh_token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        account = Account.objects.get(id=payload.get("user_id"))
        access_token, new_refresh_token = generate_token(account)
        response = JsonResponse({"access_token": access_token})
        response.set_cookie(
            "refresh_token", new_refresh_token, httponly=True, max_age=60 * 60 * 24 * 7
        )
        return response
    except Account.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=401)
    except (
        jwt.ExpiredSignatureError,
        jwt.InvalidTokenError,
        jwt.DecodeError,
        jwt.InvalidSignatureError,
    ):
        # 所有 JWT 相關錯誤統一處理
        return JsonResponse({"error": "Invalid or expired token"}, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    response = JsonResponse({"message": "Logout successfully"})
    response.delete_cookie("refresh_token", path="/")
    return response
