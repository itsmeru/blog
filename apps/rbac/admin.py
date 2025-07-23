from django.contrib import admin

from .models import Permission, Role, RoleHierarchy, RolePermission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """權限管理"""

    list_display = (
        "name",
        "code",
        "category",
        "module",
        "action",
        "resource",
        "level",
        "is_active",
    )
    list_filter = ("module", "category", "is_active")
    search_fields = ("name", "code", "description")
    ordering = ("module", "level", "code")
    list_per_page = 20


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """角色管理"""

    list_display = ("name", "code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "description")
    ordering = ("code",)
    list_per_page = 20


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """角色權限關聯管理"""

    list_display = ("role", "permission", "is_active", "created_at")
    list_filter = ("role", "permission", "is_active")
    search_fields = ("role__name", "role__code", "permission__name")
    ordering = ("role", "permission")
    list_per_page = 20


@admin.register(RoleHierarchy)
class RoleHierarchyAdmin(admin.ModelAdmin):
    """角色階層關係管理"""

    list_display = ("parent_role", "child_role", "created_at")
    list_filter = ("parent_role", "child_role")
    search_fields = (
        "parent_role__name",
        "parent_role__code",
        "child_role__name",
        "child_role__code",
    )
    ordering = ("parent_role", "child_role")
    list_per_page = 20
