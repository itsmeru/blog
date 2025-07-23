from django.urls import path

from .views import (
    PermissionBatchUpdateViewSet,
    PermissionDetailViewSet,
    PermissionViewSet,
    RoleDetailViewSet,
    RoleUsersDetailView,
    RoleUsersListView,
    RoleViewSet,
)

app_name = "rbac"

urlpatterns = [
    # 權限相關 URL
    path("permissions/", PermissionViewSet.as_view(), name="permission-list"),
    path(
        "permissions/<int:pk>/",
        PermissionDetailViewSet.as_view(),
        name="permission-detail",
    ),
    path(
        "permissions/batch-update/",
        PermissionBatchUpdateViewSet.as_view(),
        name="permission-batch-update",
    ),
    # 角色相關 URL
    path("roles/", RoleViewSet.as_view(), name="role-list"),
    path("roles/<int:pk>/", RoleDetailViewSet.as_view(), name="role-detail"),
    # 角色使用者相關 URL
    path(
        "roles/<int:role_id>/users/",
        RoleUsersDetailView.as_view(),
        name="role-users-detail",
    ),
    path("roles/users/", RoleUsersListView.as_view(), name="role-users-list"),
]
