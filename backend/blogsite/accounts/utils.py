from functools import wraps

import jwt
from accounts.models import Account
from blogsite import settings
from django.http import JsonResponse


def login_check(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "未授權，缺少 token"}, status=401)
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            account = Account.objects.get(id=user_id)
            request.account = account
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Account.DoesNotExist):
            return JsonResponse({"error": "無效或過期的 token"}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped_view
