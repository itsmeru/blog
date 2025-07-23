from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.app.base.pagination import CustomPageNumberPagination as StandardResultsSetPagination
from core.app.base.serializer import BaseErrorSerializer

from .serializers import (
    DepartmentListResponseSerializer,
    ForgotPasswordResponseSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LoginSuccessResponseSerializer,
    MeResponseSerializer,
    RefreshTokenResponseSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
    UserCreateResponseSerializer,
    UserCreateSerializer,
    UserDetailResponseSerializer,
    UserDetailSerializer,
    UserListPaginationResponseSerializer,
    UserListSerializer,
    UserPatchSerializer,
    UserUpdateResponseSerializer,
    UserUpdateSerializer,
)
from .service import UserService

# Create your views here.


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="註冊新用戶",
        request=RegisterSerializer,
        responses={
            201: RegisterSerializer,
            400: BaseErrorSerializer,
        },
        tags=["Users"],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.register_user(
            email=serializer.validated_data["email"],
            phone=serializer.validated_data.get("phone"),
            nickname=serializer.validated_data["nickname"],
            password=serializer.validated_data["password"],
        )
        return Response(data=RegisterSerializer(user).data, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="使用者登入",
        request=LoginSerializer,
        responses={200: LoginSuccessResponseSerializer, 400: BaseErrorSerializer},
        tags=["Users"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.authenticate(
            account=serializer.validated_data["account"],
            password=serializer.validated_data["password"],
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
                "nickname": user.nickname,
            }
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="重設密碼流程啟動",
        request=ForgotPasswordSerializer,
        responses={
            200: ForgotPasswordResponseSerializer,
            404: BaseErrorSerializer,
        },
        tags=["Users"],
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.start_forgot_password(serializer.validated_data["account"])
        return Response(
            data={
                "message": "重設密碼流程啟動（請串接 email/sms）",
                "user_found": bool(user),
            }
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="取得個人資料",
        responses={200: MeResponseSerializer, 401: BaseErrorSerializer},
        tags=["Users"],
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                data={"detail": "Authentication credentials were not provided."},
                status=401,
            )
        user = request.user
        return Response(
            data={
                "user_id": user.id,
                "email": user.email,
                "phone": user.phone,
                "nickname": user.nickname,
            }
        )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="刷新 Access Token",
        request=RefreshTokenSerializer,
        responses={200: RefreshTokenResponseSerializer, 400: BaseErrorSerializer},
        tags=["Users"],
    )
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = UserService.refresh_token(serializer.validated_data["refresh"])
        return Response(data)


class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Override get_queryset to provide custom filtering"""
        department = self.request.query_params.get("department")
        is_active = self.request.query_params.get("is_active")
        search = self.request.query_params.get("search")

        if is_active is not None:
            is_active = is_active.lower() == "true"

        return UserService.get_users_list(
            department=department, is_active=is_active, search=search
        )

    @extend_schema(
        summary="取得使用者列表",
        parameters=[
            OpenApiParameter(
                name="department", description="部門", required=False, type=str
            ),
            OpenApiParameter(
                name="is_active", description="是否啟用", required=False, type=bool
            ),
            OpenApiParameter(
                name="search", description="搜尋關鍵字", required=False, type=str
            ),
            OpenApiParameter(name="page", description="頁數", required=False, type=int),
            OpenApiParameter(
                name="page_size", description="每頁筆數", required=False, type=int
            ),
        ],
        responses={200: UserListPaginationResponseSerializer, 401: BaseErrorSerializer},
        tags=["User Management"],
    )
    def get(self, request):
        return super().get(request)

    @extend_schema(
        summary="新增使用者",
        request=UserCreateSerializer,
        responses={201: UserCreateResponseSerializer, 400: BaseErrorSerializer},
        tags=["User Management"],
    )
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create_user(**serializer.validated_data)
        return Response(UserListSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="取得使用者詳細資料",
        parameters=[
            OpenApiParameter(
                name="stage",
                description="前台/後台篩選",
                required=False,
                type=str,
                enum=["frontstage", "backstage"],
            ),
            OpenApiParameter(
                name="enabled",
                description="權限啟用狀態篩選",
                required=False,
                type=bool,
            ),
        ],
        responses={200: UserDetailResponseSerializer, 404: BaseErrorSerializer},
        tags=["User Management"],
    )
    def get(self, request, pk):
        user = UserService.get_user_detail(pk)
        stage = request.query_params.get("stage")
        enabled = request.query_params.get("enabled")

        # Convert enabled string to boolean if provided
        if enabled is not None:
            enabled = enabled.lower() == "true"

        # 使用 service 層準備數據
        permission_groups = UserService.get_user_permission_groups(
            user, stage=stage, enabled=enabled
        )
        permission_stats = UserService.get_user_permission_stats(
            user, stage=stage, enabled=enabled
        )


        user_data = {
            "id": user.id,
            "nickname": user.nickname,
            "department": user.department,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "roles": [
                {"id": role.id, "name": role.name, "name_zh": role.name_zh}
                for role in user.roles.all()
            ],
            "permission_groups": permission_groups,
            "total_permissions": permission_stats["total_permissions"],
            "enabled_permissions_count": permission_stats["enabled_permissions_count"],
        }

        serializer = UserDetailSerializer(user_data)
        return Response(serializer.data)

    @extend_schema(
        summary="更新使用者",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateResponseSerializer,
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["User Management"],
    )
    def put(self, request, pk):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Filter out None values to avoid setting fields to None unnecessarily
        update_data = {
            k: v for k, v in serializer.validated_data.items() if v is not None
        }

        user = UserService.update_user(pk, **update_data)
        return Response(UserListSerializer(user).data)

    @extend_schema(
        summary="部分更新使用者 (僅限 is_active)",
        request=UserPatchSerializer,
        responses={
            200: UserUpdateResponseSerializer,
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["User Management"],
    )
    def patch(self, request, pk):
        serializer = UserPatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = UserService.update_user(pk, is_active=serializer.validated_data["is_active"])
        return Response(UserListSerializer(user).data)

    @extend_schema(
        summary="刪除使用者 (硬刪除)",
        responses={204: None, 404: BaseErrorSerializer},
        tags=["User Management"],
    )
    def delete(self, request, pk):
        UserService.delete_user(pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DepartmentListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="取得部門選項列表",
        responses={200: DepartmentListResponseSerializer, 401: BaseErrorSerializer},
        tags=["User Management"],
    )
    def get(self, request):
        departments = UserService.get_department_options()
        return Response(departments)
