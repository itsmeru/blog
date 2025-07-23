from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.rbac.models import Permission, Role
from apps.rbac.repositories import (
    PermissionRepository,
    RoleHierarchyRepository,
    RolePermissionRepository,
    RoleRepository,
    UserPermissionRepository,
)

from .seeders import RBACSeeder


class PermissionRepositoryTest(TestCase):
    """權限資料存取層測試"""

    def setUp(self):
        self.seed_data = RBACSeeder.seed_all()
        self.permission = self.seed_data["permissions"][0]

    def test_get_by_id(self):
        """測試根據 ID 獲取權限"""
        permission = PermissionRepository.get_by_id(self.permission.id)
        self.assertEqual(permission.id, self.permission.id)
        self.assertEqual(permission.code, self.permission.code)

    def test_get_by_code(self):
        """測試根據權限代碼獲取權限"""
        permission = PermissionRepository.get_by_code(self.permission.code)
        self.assertEqual(permission.id, self.permission.id)

    def test_get_all(self):
        """測試獲取所有權限"""
        permissions = PermissionRepository.get_all()
        self.assertEqual(permissions.count(), len(self.seed_data["permissions"]))

    def test_get_active(self):
        """測試獲取所有啟用的權限"""
        # 停用一個權限
        permission = Permission.objects.get(id=self.seed_data["permissions"][0].id)
        permission.is_active = False
        permission.save()

        permissions = PermissionRepository.get_active()
        self.assertEqual(permissions.count(), len(self.seed_data["permissions"]) - 1)

    def test_get_by_module(self):
        """測試獲取指定模組的權限"""
        permissions = PermissionRepository.get_by_module(self.permission.module)
        self.assertEqual(permissions.count(), len(self.seed_data["permissions"]))

    def test_create(self):
        """測試建立權限"""
        permission_data = {
            "code": "test:create",
            "name": "測試建立",
            "category": "test",
            "module": "test",
            "action": "create",
            "resource": "test",
            "level": 1,
        }
        permission = PermissionRepository.create(**permission_data)
        self.assertEqual(permission.code, permission_data["code"])
        self.assertEqual(permission.name, permission_data["name"])

    def test_update(self):
        """測試更新權限"""
        permission = Permission.objects.get(id=self.permission.id)
        updated_data = {"name": "更新後的權限名稱", "description": "更新後的描述"}
        permission = PermissionRepository.update(permission, **updated_data)
        self.assertEqual(permission.name, updated_data["name"])
        self.assertEqual(permission.description, updated_data["description"])

    def test_delete(self):
        """測試刪除權限"""
        permission = Permission.objects.get(id=self.permission.id)
        PermissionRepository.delete(permission)
        self.assertFalse(Permission.objects.filter(id=self.permission.id).exists())


class RoleRepositoryTest(TestCase):
    """角色資料存取層測試"""

    def setUp(self):
        self.seed_data = RBACSeeder.seed_all()
        self.role = self.seed_data["roles"][0]

    def test_get_by_id(self):
        """測試根據 ID 獲取角色"""
        role = RoleRepository.get_by_id(self.role.id)
        self.assertEqual(role.id, self.role.id)
        self.assertEqual(role.code, self.role.code)

    def test_get_by_code(self):
        """測試根據角色代碼獲取角色"""
        role = RoleRepository.get_by_code(self.role.code)
        self.assertEqual(role.id, self.role.id)

    def test_get_all(self):
        """測試獲取所有角色"""
        roles = RoleRepository.get_all()
        self.assertEqual(roles.count(), len(self.seed_data["roles"]))

    def test_get_active(self):
        """測試獲取所有啟用的角色"""
        # 停用一個角色
        role = Role.objects.get(id=self.seed_data["roles"][0].id)
        role.is_active = False
        role.save()

        roles = RoleRepository.get_active()
        self.assertEqual(roles.count(), len(self.seed_data["roles"]) - 1)

    def test_create(self):
        """測試建立角色"""
        role_data = {
            "code": "test:role",
            "name": "測試角色",
            "category": "test",
            "level": 1,
            "description": "測試角色描述",
        }
        role = RoleRepository.create(**role_data)
        self.assertEqual(role.code, role_data["code"])
        self.assertEqual(role.name, role_data["name"])

    def test_update(self):
        """測試更新角色"""
        role = Role.objects.get(id=self.role.id)
        updated_data = {"name": "更新後的角色名稱", "description": "更新後的描述"}
        role = RoleRepository.update(role, **updated_data)
        self.assertEqual(role.name, updated_data["name"])
        self.assertEqual(role.description, updated_data["description"])

    def test_delete(self):
        """測試刪除角色"""
        role = Role.objects.get(id=self.role.id)
        RoleRepository.delete(role)
        self.assertFalse(Role.objects.filter(id=self.role.id).exists())


class RolePermissionRepositoryTest(TestCase):
    """角色權限關聯資料存取層測試"""

    def setUp(self):
        self.seed_data = RBACSeeder.seed_all()
        self.role = Role.objects.get(id=self.seed_data["roles"][0].id)
        self.permission = Permission.objects.get(id=self.seed_data["permissions"][0].id)
        self.role_permission = RolePermissionRepository.create(
            role=self.role, permission=self.permission
        )

    def test_get_by_role(self):
        """測試獲取角色的所有權限關聯"""
        role_permissions = RolePermissionRepository.get_by_role(self.role)
        self.assertTrue(role_permissions.filter(role=self.role).exists())

    def test_get_by_permission(self):
        """測試獲取權限的所有角色關聯"""
        role_permissions = RolePermissionRepository.get_by_permission(self.permission)
        self.assertTrue(role_permissions.filter(permission=self.permission).exists())

    def test_get_active_by_role(self):
        """測試獲取角色的所有啟用權限關聯"""
        # 停用一個權限關聯
        role_permission = RolePermissionRepository.get_by_role(self.role).first()
        role_permission.is_active = False
        role_permission.save()

        active_role_permissions = RolePermissionRepository.get_active_by_role(self.role)
        self.assertFalse(active_role_permissions.filter(id=role_permission.id).exists())

    def test_create(self):
        """測試建立角色權限關聯"""
        new_permission = Permission.objects.get(id=self.seed_data["permissions"][1].id)
        role_permission = RolePermissionRepository.create(
            role=self.role, permission=new_permission
        )
        self.assertEqual(role_permission.role, self.role)
        self.assertEqual(role_permission.permission, new_permission)

    def test_update(self):
        """測試更新角色權限關聯"""
        role_permission = RolePermissionRepository.get_by_role(self.role).first()
        updated_data = {"is_active": False}
        role_permission = RolePermissionRepository.update(
            role_permission, **updated_data
        )
        self.assertFalse(role_permission.is_active)

    def test_delete(self):
        """測試刪除角色權限關聯"""
        role_permission = RolePermissionRepository.get_by_role(self.role).first()
        RolePermissionRepository.delete(role_permission)
        self.assertFalse(
            RolePermissionRepository.get_by_role(self.role)
            .filter(id=role_permission.id)
            .exists()
        )

    def test_bulk_create(self):
        """測試批次建立角色權限關聯"""
        permissions = Permission.objects.filter(
            id__in=[p.id for p in self.seed_data["permissions"][1:]]
        )
        role_permissions = RolePermissionRepository.bulk_create(self.role, permissions)
        self.assertEqual(len(role_permissions), len(permissions))


class RoleHierarchyRepositoryTest(TestCase):
    """角色繼承關係測試"""

    def setUp(self):
        self.seed_data = RBACSeeder.seed_all()
        # 創建父角色
        self.parent_role = Role.objects.create(
            code="parent_role", name="父角色", category="test", level=1
        )
        # 創建子角色
        self.child_role = Role.objects.create(
            code="child_role", name="子角色", category="test", level=2
        )
        # 創建權限
        self.permission = Permission.objects.create(
            code="test_permission",
            name="測試權限",
            category="test",
            module="test",
            action="test",
            resource="test",
            api_url="/api/v1/test/",
            method="GET",
        )
        # 將權限分配給父角色
        RolePermissionRepository.create(
            role=self.parent_role, permission=self.permission
        )
        # 建立角色繼承關係
        RoleHierarchyRepository.create(
            parent_role=self.parent_role, child_role=self.child_role
        )
        # 創建測試用戶
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="test123", nickname="測試用戶"
        )
        # 將子角色分配給用戶
        self.user.roles.add(self.child_role)

    def test_role_inheritance(self):
        """測試角色繼承關係"""
        # 獲取用戶的權限
        permissions = UserPermissionRepository.get_user_permissions(self.user)

        # 驗證用戶是否獲得了父角色的權限
        self.assertTrue(permissions.filter(id=self.permission.id).exists())

        # 驗證用戶是否有權限訪問 API
        self.assertTrue(
            UserPermissionRepository.has_permission(
                self.user, self.permission.api_url, self.permission.method
            )
        )

    def test_role_inheritance_with_disabled_permission(self):
        """測試角色繼承關係中的權限停用"""
        # 停用父角色的權限
        role_permission = RolePermissionRepository.get_by_role(self.parent_role).first()
        RolePermissionRepository.update(role_permission, is_active=False)

        # 獲取用戶的權限
        permissions = UserPermissionRepository.get_user_permissions(self.user)

        # 驗證用戶是否失去了權限
        self.assertFalse(permissions.filter(id=self.permission.id).exists())

        # 驗證用戶是否無法訪問 API
        self.assertFalse(
            UserPermissionRepository.has_permission(
                self.user, self.permission.api_url, self.permission.method
            )
        )

    def test_role_inheritance_with_multiple_levels(self):
        """測試多層級的角色繼承關係"""
        # 創建孫角色
        grandchild_role = Role.objects.create(
            code="grandchild_role", name="孫角色", category="test", level=3
        )

        # 建立子角色和孫角色的繼承關係
        RoleHierarchyRepository.create(
            parent_role=self.child_role, child_role=grandchild_role
        )

        # 創建新用戶並分配孫角色
        new_user = get_user_model().objects.create_user(
            email="new_test@example.com", password="test123", nickname="新測試用戶"
        )
        new_user.roles.add(grandchild_role)

        # 獲取新用戶的權限
        permissions = UserPermissionRepository.get_user_permissions(new_user)

        # 驗證新用戶是否獲得了父角色的權限
        self.assertTrue(permissions.filter(id=self.permission.id).exists())

        # 驗證新用戶是否有權限訪問 API
        self.assertTrue(
            UserPermissionRepository.has_permission(
                new_user, self.permission.api_url, self.permission.method
            )
        )


class UserPermissionRepositoryTest(TestCase):
    """用戶權限資料存取層測試"""

    @classmethod
    def setUpTestData(cls):
        seed_data = RBACSeeder.seed_all()
        cls.user = get_user_model().objects.get(
            id=seed_data["users"][1].id
        )  # 使用 normal_user
        cls.role = Role.objects.get(id=seed_data["roles"][1].id)  # 使用 user_role
        cls.permission = Permission.objects.get(
            id=seed_data["permissions"][1].id
        )  # 使用用戶管理權限
        cls.user.roles.add(cls.role)
        RolePermissionRepository.create(role=cls.role, permission=cls.permission)
        # 清除 enabled_permissions
        cls.user.enabled_permissions = []
        cls.user.save()
        cls.seed_data = seed_data

    def test_get_user_permissions(self):
        """測試獲取用戶的所有權限"""
        permissions = UserPermissionRepository.get_user_permissions(self.user)
        self.assertTrue(permissions.filter(id=self.permission.id).exists())

    def test_has_permission(self):
        """測試檢查用戶是否有權限"""
        # 測試用戶有權限的情況
        self.assertTrue(
            UserPermissionRepository.has_permission(
                self.user, self.permission.api_url, self.permission.method
            )
        )

        # 測試用戶沒有權限的情況
        new_permission = Permission.objects.get(
            id=self.seed_data["permissions"][0].id
        )  # 使用 permission_list
        self.assertFalse(
            UserPermissionRepository.has_permission(
                self.user, new_permission.api_url, new_permission.method
            )
        )

    def test_clear_user_permissions_cache(self):
        """測試清除用戶權限快取"""
        # 先獲取一次權限，這會設置快取
        UserPermissionRepository.get_user_permissions(self.user)

        # 清除快取
        UserPermissionRepository.clear_user_permissions_cache(self.user)

        # 再次獲取權限，應該會從數據庫重新獲取
        permissions = UserPermissionRepository.get_user_permissions(self.user)
        self.assertTrue(permissions.filter(id=self.permission.id).exists())
