from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.app.base.serializer import BaseErrorSerializer, DeleteSuccessSerializer

from .models import Role, RoleHierarchy
from .serializers import (
    PermissionBatchUpdateOkResponseSerializer,
    PermissionBatchUpdateSerializer,
    PermissionDetailResponseSerializer,
    PermissionListResponseSerializer,
    PermissionSerializer,
    RoleCreateSerializer,
    RoleDetailSerializer,
    RoleHierarchySerializer,
    RoleListSerializer,
    RoleManagementDetailResponseSerializer,
    RoleManagementListResponseSerializer,
    RoleUpdateSerializer,
    RoleUserListResponseSerializer,
    RoleUsersDetailResponseSerializer,
    RoleUsersUpdateSerializer,
)
from .services import (
    PermissionService,
    RoleService,
    RoleUserService,
)

# Create your views here.


class PermissionViewSet(APIView):
    @extend_schema(
        summary="取得權限列表",
        operation_id="list_permissions",
        parameters=[
            OpenApiParameter(
                name="stage",
                description="前台/後台 (frontstage/backstage)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_active",
                description="是否啟用 (true/false)",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="search",
                description="搜尋功能名稱",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: PermissionListResponseSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def get(self, request):
        stage = request.query_params.get("stage")
        is_active = request.query_params.get("is_active")
        search = request.query_params.get("search")

        if is_active is not None:
            is_active = is_active.lower() == "true"

        data = PermissionService.get_permissions_grouped(
            stage=stage, is_active=is_active, function_zh_search=search
        )
        serializer = PermissionListResponseSerializer(data)
        return Response(data=serializer.data)

    @extend_schema(
        summary="建立權限",
        request=PermissionSerializer,
        responses={
            201: PermissionDetailResponseSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def post(self, request):
        serializer = PermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permission = PermissionService.create_permission(**serializer.validated_data)
        return Response(data=PermissionSerializer(permission).data, status=201)


class PermissionDetailViewSet(APIView):
    @extend_schema(
        summary="取得權限詳細資訊",
        operation_id="retrieve_permission",
        responses={
            200: PermissionDetailResponseSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def get(self, request, pk):
        permission = PermissionService.get_permission(pk)
        return Response(data=PermissionSerializer(permission).data)

    @extend_schema(
        summary="更新權限",
        request=PermissionSerializer,
        responses={
            200: PermissionDetailResponseSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def patch(self, request, pk):
        permission = PermissionService.get_permission(pk)
        serializer = PermissionSerializer(permission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        permission = PermissionService.update_permission(
            pk, **serializer.validated_data
        )
        return Response(data=PermissionSerializer(permission).data)

    @extend_schema(
        summary="刪除權限",
        responses={
            200: DeleteSuccessSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def delete(self, request, pk):
        PermissionService.delete_permission(pk)
        return Response()


class RoleViewSet(APIView):
    @extend_schema(
        summary="取得角色列表",
        operation_id="list_roles",
        responses={
            200: RoleManagementListResponseSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Role"],
    )
    def get(self, request):
        # Service layer call
        role_service = RoleService()
        roles = role_service.get_roles_with_user_count()

        # Serialization layer
        serializer = RoleListSerializer(roles, many=True)

        response_data = {"roles": serializer.data, "total": len(roles)}

        return Response(data=response_data)

    @extend_schema(
        summary="建立角色",
        request=RoleCreateSerializer,
        responses={
            201: RoleManagementDetailResponseSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Role"],
    )
    def post(self, request):
        # Serialization layer - validation
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Service layer call
        role_service = RoleService()
        role = role_service.create_role_with_permissions(
            validated_data,
        )

        # Get role with user count for response
        role_with_count = role_service.get_role_with_user_count(role.id)

        # Service layer - get business data
        permission_groups = role_service.get_role_permission_groups(role.id)
        permission_stats = role_service.get_role_permission_stats(role.id)

        # Prepare data for serializer
        role_data = {
            "id": role_with_count.id,
            "code": role_with_count.code,
            "name_zh": role_with_count.name_zh,
            "is_active": role_with_count.is_active,
            "permission_groups": permission_groups,
            "total_apply_users": role_with_count.total_apply_users,
            **permission_stats,
        }

        # Serialization layer - pure serialization
        detail_serializer = RoleDetailSerializer(data=role_data)
        detail_serializer.is_valid(raise_exception=True)
        return Response(data=detail_serializer.validated_data, status=201)


class RoleDetailViewSet(APIView):
    @extend_schema(
        summary="取得角色詳細資訊",
        operation_id="retrieve_role",
        parameters=[
            OpenApiParameter(
                name="stage",
                description="權限前台/後台過濾 (frontstage/backstage)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_active",
                description="權限啟用/禁用過濾 (true/false)",
                required=False,
                type=bool,
            ),
        ],
        responses={
            200: RoleManagementDetailResponseSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Role"],
    )
    def get(self, request, pk):
        # Get query parameters for permission filtering
        stage = request.query_params.get("stage")
        is_active = request.query_params.get("is_active")

        if is_active is not None:
            is_active = bool(is_active.lower() == "true")

        # Service layer calls
        role_service = RoleService()
        role = role_service.get_role_with_user_count(pk)

        if not role:
            return Response({"detail": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)

        # Service layer - get business data with filtering
        permission_groups = role_service.get_role_permission_groups(
            pk, stage=stage, is_active=is_active
        )
        permission_stats = role_service.get_role_permission_stats(pk, stage=stage)

        # Prepare data for serializer
        role_data = {
            "id": role.id,
            "code": role.code,
            "is_active": role.is_active,
            "name_zh": role.name_zh,
            "permission_groups": permission_groups,
            "total_apply_users": role.total_apply_users,
            **permission_stats,
        }

        # Serialization layer - pure serialization
        serializer = RoleDetailSerializer(data=role_data)
        serializer.is_valid(raise_exception=True)
        return Response(data=serializer.validated_data)

    @extend_schema(
        summary="更新角色",
        request=RoleUpdateSerializer,
        responses={
            200: RoleManagementDetailResponseSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Role"],
    )
    def put(self, request, pk):
        # Serialization layer - validation
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Service layer call
        role_service = RoleService()
        try:
            role = role_service.update_role_with_permissions(
                pk,
                validated_data,
            )

            # Get role with user count for response
            role_with_count = role_service.get_role_with_user_count(role.id)

            # Service layer - get business data
            permission_groups = role_service.get_role_permission_groups(role.id)
            permission_stats = role_service.get_role_permission_stats(role.id)

            # Prepare data for serializer
            role_data = {
                "id": role_with_count.id,
                "code": role_with_count.code,
                "name_zh": role_with_count.name_zh,
                "is_active": role_with_count.is_active,
                "permission_groups": permission_groups,
                "total_apply_users": role_with_count.total_apply_users,
                **permission_stats,
            }

            # Serialization layer - pure serialization
            detail_serializer = RoleDetailSerializer(data=role_data)
            detail_serializer.is_valid(raise_exception=True)
            return Response(data=detail_serializer.validated_data)

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="刪除角色",
        responses={
            200: DeleteSuccessSerializer,
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Role"],
    )
    def delete(self, request, pk):
        RoleService.delete_role_safe(pk)
        return Response({"message": "角色刪除成功"})


class RoleHierarchyViewSet(viewsets.ModelViewSet):
    """角色階層關係視圖集"""

    queryset = RoleHierarchy.objects.all()
    serializer_class = RoleHierarchySerializer
    filterset_fields = ["parent_role", "child_role"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        """建立前檢查是否會形成循環依賴"""
        parent_role = serializer.validated_data["parent_role"]
        child_role = serializer.validated_data["child_role"]

        if self._would_create_cycle(parent_role, child_role):
            raise serializers.ValidationError("不能建立循環依賴的角色階層關係")

        serializer.save()

    def _would_create_cycle(self, parent_role, child_role):
        """檢查是否會形成循環依賴"""

        # 如果父角色是子角色的子孫，就會形成循環
        def get_all_children(role, visited=None):
            if visited is None:
                visited = set()
            visited.add(role.id)
            children = Role.objects.filter(parents__parent_role=role)
            for child in children:
                if child.id not in visited:
                    get_all_children(child, visited)
            return visited

        # 獲取子角色的所有子孫
        children = get_all_children(child_role)
        # 如果父角色在子孫中，就會形成循環
        return parent_role.id in children


class PermissionBatchUpdateViewSet(APIView):
    @extend_schema(
        summary="批次更新權限啟用狀態",
        request=PermissionBatchUpdateSerializer,
        responses={
            200: PermissionBatchUpdateOkResponseSerializer,
            400: BaseErrorSerializer,
            401: BaseErrorSerializer,
        },
        tags=["RBAC: Permission"],
    )
    def patch(self, request):
        serializer = PermissionBatchUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        permission_ids = serializer.validated_data["permission_ids"]
        is_active = serializer.validated_data["is_active"]

        updated_count = PermissionService.batch_update_permissions(
            permission_ids=permission_ids, is_active=is_active
        )

        return Response(
            {
                "updated_count": updated_count,
                "message": f"已更新 {updated_count} 個權限",
            },
            status=status.HTTP_200_OK,
        )


class RoleUsersDetailView(APIView):
    """角色使用者詳情檢視"""

    @extend_schema(
        summary="取得角色使用者詳情",
        description="取得指定角色的使用者列表資訊",
        responses={
            200: RoleUsersDetailResponseSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Role Users"],
    )
    def get(self, request, role_id):
        try:
            role_users_data = RoleUserService.get_role_users(role_id)
            return Response(role_users_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="更新角色使用者列表",
        description="更新指定角色的使用者列表",
        request=RoleUsersUpdateSerializer,
        responses={
            200: {"description": "更新成功"},
            400: BaseErrorSerializer,
            404: BaseErrorSerializer,
        },
        tags=["RBAC: Role Users"],
    )
    def put(self, request, role_id):
        serializer = RoleUsersUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_ids = serializer.validated_data["user_ids"]
            RoleUserService.update_role_users(role_id, user_ids)
            return Response(
                {"message": "角色使用者更新成功"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RoleUsersListView(APIView):
    """角色使用者列表檢視"""

    @extend_schema(
        summary="取得所有使用者列表",
        description="取得可供角色分配的使用者列表，支援分頁、搜尋和部門篩選",
        parameters=[
            OpenApiParameter(
                name="search",
                description="搜尋關鍵字 (暱稱或郵箱)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="department",
                description="部門篩選",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="page",
                description="頁碼",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="page_size",
                description="每頁數量",
                required=False,
                type=int,
            ),
        ],
        responses={
            200: RoleUserListResponseSerializer,
        },
        tags=["RBAC: Role Users"],
    )
    def get(self, request):
        search = request.query_params.get("search")
        department = request.query_params.get("department")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))

        users_data = RoleUserService.get_role_users_list(
            search=search, department=department, page=page, page_size=page_size
        )

        return Response(users_data, status=status.HTTP_200_OK)
