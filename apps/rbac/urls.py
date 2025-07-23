from django.urls import path

from .views import (
    PermissionCreateListView,
    PermissionDetailView,
    PermissionBatchUpdateView,
    RoleCreateListView,
    RoleDetailView,
    RoleUsersDetailView,
    RoleUsersListView,
)

app_name = "rbac"

urlpatterns = [
    path("permissions/", PermissionCreateListView.as_view(), name="permission-list"),
    path(
        "permissions/<int:pk>/",
        PermissionDetailView.as_view(),
        name="permission-detail",
    ),
    path(
        "permissions/batch-update/",
        PermissionBatchUpdateView.as_view(),
        name="permission-batch-update",
    ),
    path("roles/", RoleCreateListView.as_view(), name="role-list"),
    path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
    path(
        "roles/<int:role_id>/users/",
        RoleUsersDetailView.as_view(),
        name="role-users-detail",
    ),
    path("roles/users/", RoleUsersListView.as_view(), name="role-users-list"),
]
