import logging
import traceback

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import (
    APIException,
)
from rest_framework.exceptions import (
    AuthenticationFailed as DRFAuthenticationFailed,
)
from rest_framework.exceptions import (
    NotFound as DRFNotFound,
)
from rest_framework.exceptions import (
    PermissionDenied as DRFPermissionDenied,
)
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("django")


class BaseAPIException(Exception):
    """基礎 API 異常類"""

    status_code = 500
    default_data = None
    default_errors = {"detail": "Internal Server Error"}
    default_message = "Internal Server Error"

    def __init__(self, data=None, errors=None, message=None):
        self.data = data or self.default_data
        self.errors = errors or self.default_errors
        self.message = message or self.default_message


class ValidationError(BaseAPIException):
    """驗證錯誤"""

    status_code = 400
    default_data = None
    default_errors = {"detail": "Validation Error"}
    default_message = "Validation Error"


class NotFoundError(BaseAPIException):
    """找不到資源錯誤"""

    status_code = 404
    default_data = None
    default_errors = {"detail": "Not Found"}
    default_message = "Not Found"


class PermissionDeniedError(BaseAPIException):
    """權限拒絕錯誤"""

    status_code = 403
    default_data = None
    default_errors = {"detail": "Permission Denied"}
    default_message = "Permission Denied"


class AuthenticationError(BaseAPIException):
    """認證錯誤"""

    status_code = 401
    default_data = None
    default_errors = {"detail": "Authentication Failed"}
    default_message = "Authentication Failed"


class PayloadTooLargeError(BaseAPIException):
    """請求大小超出限制"""

    status_code = 413
    default_data = None
    default_errors = {"detail": "Payload too large"}
    default_message = "Payload too large"


class ServerError(BaseAPIException):
    """伺服器錯誤"""

    status_code = 500
    default_data = None
    default_errors = {"detail": "Internal Server Error"}
    default_message = "Internal Server Error"


class BusinessError(BaseAPIException):
    """業務邏輯錯誤"""

    status_code = 400
    default_data = None
    default_errors = {"detail": "Business Error"}
    default_message = "Business Error"


class ServiceUnavailableError(BaseAPIException):
    """服務不可用錯誤"""

    status_code = 503
    default_data = None
    default_errors = {"detail": "Service Unavailable"}
    default_message = "Service Unavailable"


def custom_exception_handler(exc, context):
    """自定義異常處理器"""
    response = exception_handler(exc, context)

    message = "Internal Server Error"
    status = 500
    errors = []
    data = None

    if isinstance(exc, BaseAPIException):
        status = exc.status_code
        message = exc.message
        errors = exc.errors
        data = exc.data
    elif isinstance(exc, DjangoValidationError):
        status = 400
        message = "Validation Error"
        if hasattr(exc, "message_dict"):
            errors = exc.message_dict
        elif hasattr(exc, "error_list"):
            errors = [error.message for error in exc.error_list]
        else:
            errors = [str(exc.message)]
    elif isinstance(exc, DRFPermissionDenied):
        status = 403
        message = "Permission Denied"
        errors = [str(exc.detail)]
    elif isinstance(exc, APIException):
        match exc:
            case DRFValidationError():
                message = "Validation Error"
            case DRFNotFound():
                message = "Not Found"
            case DRFAuthenticationFailed():
                message = "Authentication Failed"
        status = response.status_code
        errors = response.data
    else:
        traceback_str = traceback.format_exc()
        logger.error(
            f"Unknown Exception: {exc}, traceback: {traceback_str}",
            extra={
                "exc": exc,
                "context": context,
                "traceback": traceback_str,
            },
        )
    if response is None:
        response = Response(
            {
                "success": False,
                "message": message,
                "errors": errors,
                "data": data,
            },
            status=status,
        )
    response.exception = True
    response.context = {
        "success": False,
        "message": message,
        "errors": errors,
        "data": data,
    }
    return response
