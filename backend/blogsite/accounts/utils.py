from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def login_check(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "未授權，請先登入"}, status=status.HTTP_401_UNAUTHORIZED)
        
        return view_func(self, request, *args, **kwargs)
    
    return _wrapped_view
