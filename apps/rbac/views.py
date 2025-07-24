from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from apps.rbac.models import Role

from core.app.base.serializer import BaseErrorSerializer, DeleteSuccessSerializer
from .serializers import (
    PermissionSerializer,
    RoleSimpleSerializer,
    RoleDetailSerializer,
    RoleUserSerializer,
    PermissionSuccessResponseSerializer,
    PermissionListResponseSerializer,
    RoleDetailResponseSerializer,
    RoleListResponseSerializer,
    RoleUserListResponseSerializer,
    BaseSuccessResponseSerializer,
    RoleUsersDetailSerializer,
    RoleUsersUpdateSerializer,
    PermissionBatchUpdateSerializer,
)
from apps.rbac.services.role_service import RoleService
from apps.rbac.services.permission_service import PermissionService


class PermissionCreateListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: PermissionListResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="取得所有權限",
        tags=["RBAC: Permission"],
    )
    def get(self, request):
        permissions = PermissionService.list_permissions()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": serializer.data,
            }
        )

    @extend_schema(
        request=PermissionSerializer,
        responses={
            201: PermissionSuccessResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="建立權限",
        tags=["RBAC: Permission"],
    )
    def post(self, request):
        permission = PermissionService.create_permission(request.data)
        return Response(
            {
                "success": True,
                "message": "權限建立成功",
                "data": PermissionSerializer(permission).data,
            },
            status=status.HTTP_201_CREATED,
        )


# 權限細節
class PermissionDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: PermissionSuccessResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="取得權限細節",
        tags=["RBAC: Permission"],
    )
    def get(self, request, pk):
        permission = PermissionService.get_permission(pk)
        serializer = PermissionSerializer(permission)
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": serializer.data,
            }
        )

    @extend_schema(
        request=PermissionSerializer,
        responses={
            200: PermissionSuccessResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="更新權限",
        tags=["RBAC: Permission"],
    )
    def patch(self, request, pk):
        permission = PermissionService.update_permission(pk, request.data)
        return Response(
            {
                "success": True,
                "message": "權限更新成功",
                "data": PermissionSerializer(permission).data,
            }
        )

    @extend_schema(
        responses={
            200: DeleteSuccessSerializer,
            401: BaseErrorSerializer,
        },
        summary="刪除權限",
        tags=["RBAC: Permission"],
    )
    def delete(self, request, pk):
        PermissionService.delete_permission(pk)
        return Response()


# 批次更新權限
class PermissionBatchUpdateView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PermissionBatchUpdateSerializer,
        responses={
            200: BaseSuccessResponseSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def patch(self, request):
        permission_ids = request.data.get("permission_ids", [])
        is_active = request.data.get("is_active", True)
        count = PermissionService.batch_update_permissions(permission_ids, is_active)
        return Response(
            {
                "success": True,
                "message": f"已更新 {count} 筆權限",
                "data": {},
            }
        )


# 角色列表與建立
class RoleCreateListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: RoleListResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="取得所有角色",
        tags=["RBAC: Role"],
    )
    def get(self, request):
        roles = RoleService.list_roles()
        serializer = RoleSimpleSerializer(roles, many=True)
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": {"roles": serializer.data, "total": len(serializer.data)},
            }
        )

    @extend_schema(
        request=RoleSimpleSerializer,
        responses={
            201: RoleDetailResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="建立角色",
        tags=["RBAC: Role"],
    )
    def post(self, request):
        permissions = request.data.pop("permissions", [])
        role = RoleService.create_role(request.data, permissions)
        serializer = RoleDetailSerializer(role)
        return Response(
            {
                "success": True,
                "message": "角色建立成功",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


# 角色細節
class RoleDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: RoleDetailResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="取得角色細節",
        tags=["RBAC: Role"],
    )
    def get(self, request, pk):
        role = RoleService.get_role(pk)
        serializer = RoleDetailSerializer(role)
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": serializer.data,
            }
        )

    @extend_schema(
        request=RoleSimpleSerializer,
        responses={
            200: RoleDetailResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="更新角色",
        tags=["RBAC: Role"],
    )
    def put(self, request, pk):
        permissions = request.data.pop("permissions", [])
        role = RoleService.update_role(pk, request.data, permissions)
        serializer = RoleDetailSerializer(role)
        return Response(
            {
                "success": True,
                "message": "角色更新成功",
                "data": serializer.data,
            }
        )

    @extend_schema(
        responses={
            200: DeleteSuccessSerializer,
            401: BaseErrorSerializer,
        },
        summary="刪除角色",
        tags=["RBAC: Role"],
    )
    def delete(self, request, pk):
        RoleService.delete_role(pk)
        return Response()


# 角色使用者細節
class RoleUsersDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="取得角色使用者詳情",
        responses={
            200: RoleUsersDetailSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Role Users"],
    )
    def get(self, request, role_id):
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response(
                {"success": False, "message": "角色不存在", "data": None}, status=404
            )
        users = role.users.all()
        serializer = RoleUsersDetailSerializer(
            {
                "id": role.id,
                "name_zh": role.name_zh,
                "total_user": users.count(),
                "users": [
                    {
                        "id": u.id,
                        "nickname": u.nickname,
                        "email": u.email,
                        "is_active": u.is_active,
                    }
                    for u in users
                ],
            }
        )
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": {
                    "id": role.id,
                    "name_zh": role.name_zh,
                    "total_user": users.count(),
                },
            }
        )

    @extend_schema(
        summary="更新角色使用者列表",
        request=RoleUsersUpdateSerializer,
        responses={
            200: {"description": "更新成功"},
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Role Users"],
    )
    def put(self, request, role_id):
        serializer = RoleUsersUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_ids = serializer.validated_data["user_ids"]
        RoleService.set_role_users(role_id, user_ids)
        return Response(
            {
                "success": True,
                "message": "角色使用者更新成功",
                "data": None,
            }
        )


# 角色使用者列表
class RoleUsersListView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: RoleUserListResponseSerializer,
            401: BaseErrorSerializer,
        },
        summary="取得所有角色使用者",
        tags=["RBAC: Role Users"],
    )
    def get(self, request):
        users = RoleService.list_all_role_users()
        serializer = RoleUserSerializer(users, many=True)
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "data": serializer.data,
            }
        )
