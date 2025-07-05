from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Account

# Create your views here.
@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        # 解析 JSON 數據
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        # 驗證必填欄位
        if not all([username, email, password]):
            return JsonResponse({
                'success': False,
                'message': f'所有欄位都是必填的。'
            }, status=400)
        
        # 檢查用戶名是否已存在
        if Account.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': '用戶名已存在'
            }, status=400)
        
        # 檢查郵箱是否已存在
        if Account.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': '郵箱已被註冊'
            }, status=400)
        
        # 創建新用戶
        account = Account.objects.create(
            username=username,
            email=email
        )
        # 使用自定義的密碼加密方法
        account.set_password(password)
        account.save()
        
        return JsonResponse({
            'success': True,
            'message': '註冊成功',
            'user': {
                'id': account.id,
                'username': account.username,
                'email': account.email
            }
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        print(f"請求體: {request.body}")
        return JsonResponse({
            'success': False,
            'message': f'無效的 JSON 格式: {str(e)}'
        }, status=400)
    except Exception as e:
        print(f"註冊異常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'註冊失敗: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        # 解析 JSON 數據
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        # 驗證必填欄位
        if not email or not password:
            return JsonResponse({
                'success': False,
                'message': '用戶名和密碼都是必填的'
            }, status=400)
        
        # 查找用戶
        try:
            account = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '用戶名或密碼錯誤'
            }, status=401)
        
        # 驗證密碼
        if not account.check_password(password):
            return JsonResponse({
                'success': False,
                'message': '用戶名或密碼錯誤'
            }, status=401)
        
        # 生成簡單的 token（這裡可以改用 JWT）
        import hashlib
        import time
        token_data = f"{account.username}{account.id}{time.time()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        
        return JsonResponse({
            'success': True,
            'message': '登入成功',
            'token': token,
            'user': {
                'id': account.id,
                'username': account.username,
                'email': account.email
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '無效的 JSON 格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'登入失敗: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def profile(request):
    # 這裡需要實現 token 驗證
    # 暫時返回測試數據
    return JsonResponse({
        'success': True,
        'user': {
            'id': 1,
            'username': 'test_user',
            'email': 'test@example.com'
        }
    })