from django.contrib.auth import get_user_model

from apps.rbac.models import Permission, Role

User = get_user_model()


class RBACSeeder:
    """RBAC 測試資料生成器"""

    _test_data = None

    @classmethod
    def get_test_data(cls):
        """獲取測試資料"""
        if cls._test_data is None:
            cls._test_data = cls.seed_all()
        return cls._test_data

    @classmethod
    def seed_all(cls):
        """生成所有測試資料"""
        # 創建權限
        permissions = cls._seed_permissions()

        # 創建角色
        roles = cls._seed_roles(permissions)

        # 創建用戶
        users = cls._seed_users(roles, permissions)

        return {"permissions": permissions, "roles": roles, "users": users}

    @classmethod
    def _seed_permissions(cls):
        """建立權限"""
        permissions = []

        # 權限管理相關權限
        permission_permissions = [
            {
                "code": "permission_list",
                "name": "列出權限列表",
                "category": "permission",
                "module": "rbac",
                "action": "list",
                "resource": "permission",
                "api_url": "/api/v1/rbac/permissions/",
                "method": "GET",
            },
            {
                "code": "permission_create",
                "name": "建立權限",
                "category": "permission",
                "module": "rbac",
                "action": "create",
                "resource": "permission",
                "api_url": "/api/v1/rbac/permissions/",
                "method": "POST",
            },
            {
                "code": "permission_update",
                "name": "更新權限",
                "category": "permission",
                "module": "rbac",
                "action": "update",
                "resource": "permission",
                "api_url": "/api/v1/rbac/permissions/{id}/",
                "method": "PATCH",
            },
            {
                "code": "permission_delete",
                "name": "刪除權限",
                "category": "permission",
                "module": "rbac",
                "action": "delete",
                "resource": "permission",
                "api_url": "/api/v1/rbac/permissions/{id}/",
                "method": "DELETE",
            },
        ]

        # 角色管理相關權限
        role_permissions = [
            {
                "code": "role_list",
                "name": "列出角色列表",
                "category": "role",
                "module": "rbac",
                "action": "list",
                "resource": "role",
                "api_url": "/api/v1/rbac/roles/",
                "method": "GET",
            },
            {
                "code": "role_create",
                "name": "建立角色",
                "category": "role",
                "module": "rbac",
                "action": "create",
                "resource": "role",
                "api_url": "/api/v1/rbac/roles/",
                "method": "POST",
            },
            {
                "code": "role_update",
                "name": "更新角色",
                "category": "role",
                "module": "rbac",
                "action": "update",
                "resource": "role",
                "api_url": "/api/v1/rbac/roles/{id}/",
                "method": "PATCH",
            },
            {
                "code": "role_delete",
                "name": "刪除角色",
                "category": "role",
                "module": "rbac",
                "action": "delete",
                "resource": "role",
                "api_url": "/api/v1/rbac/roles/{id}/",
                "method": "DELETE",
            },
            {
                "code": "role_get_permissions",
                "name": "獲取角色權限",
                "category": "role",
                "module": "rbac",
                "action": "get_permissions",
                "resource": "role",
                "api_url": "/api/v1/rbac/roles/{id}/permissions/",
                "method": "GET",
            },
            {
                "code": "role_set_permissions",
                "name": "設定角色權限",
                "category": "role",
                "module": "rbac",
                "action": "set_permissions",
                "resource": "role",
                "api_url": "/api/v1/rbac/roles/{id}/set-permissions/",
                "method": "POST",
            },
        ]

        # 建立權限
        for permission_data in permission_permissions + role_permissions:
            permission = Permission.objects.create(
                code=permission_data["code"],
                name=permission_data["name"],
                category=permission_data["category"],
                module=permission_data["module"],
                action=permission_data["action"],
                resource=permission_data["resource"],
                api_url=permission_data["api_url"],
                method=permission_data["method"],
                is_active=True,
                level=1,
                function_zh=permission_data["name"],  # Add function_zh field
            )
            permissions.append(permission)

        return permissions

    @classmethod
    def _seed_roles(cls, permissions):
        """生成角色測試資料"""
        roles = []

        # 系統管理員角色
        admin_role = Role.objects.create(
            code="admin",
            name="Administrator",
            name_zh="系統管理員",
            description="系統管理員角色",
            is_active=True,
            category="system",
            level=1,
        )
        admin_role.permissions.add(*permissions)
        roles.append(admin_role)

        # 一般用戶角色
        user_role = Role.objects.create(
            code="user",
            name="User",
            name_zh="一般用戶",
            description="一般用戶角色",
            is_active=True,
            category="user",
            level=2,
        )
        user_role.permissions.add(permissions[1])  # 只添加用戶管理權限
        roles.append(user_role)

        # 新增第三個角色用於測試角色階層
        test_role = Role.objects.create(
            code="test",
            name="Test Role",
            name_zh="測試角色",
            description="測試角色",
            is_active=True,
            category="test",
            level=3,
        )
        test_role.permissions.add(permissions[2])  # 添加一個權限
        roles.append(test_role)

        return roles

    @classmethod
    def _seed_users(cls, roles, permissions):
        """生成用戶測試資料"""
        users = []

        # 系統管理員用戶
        admin_user = User.objects.create_user(
            email="admin@example.com",
            password="admin123",
            nickname="Admin",
            is_active=True,
        )
        admin_user.enabled_permissions = [
            {"role": roles[0].id},  # 添加系統管理員角色
            *[{"permission": p.id} for p in permissions],  # 添加所有權限
        ]
        admin_user.save()
        users.append(admin_user)

        # 一般用戶
        normal_user = User.objects.create_user(
            email="user@example.com",
            password="user123",
            nickname="User",
            is_active=True,
        )
        normal_user.enabled_permissions = [
            {"role": roles[1].id},  # 添加一般用戶角色
            {"permission": permissions[1].id},  # 只添加用戶管理權限
        ]
        normal_user.save()
        users.append(normal_user)

        return users
