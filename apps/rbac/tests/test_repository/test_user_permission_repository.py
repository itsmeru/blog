from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.rbac.models import Permission, Role
from apps.rbac.repositories import UserPermissionRepository

User = get_user_model()


class UserPermissionRepositoryTest(TestCase):
    """使用者權限資料存取層測試"""

    def setUp(self):
        """測試前準備"""
        self.repository = UserPermissionRepository()

        # 創建測試用戶
        self.user = User.objects.create_user(
            email="test@example.com",
            password="test_password",
            nickname="test_user",
            phone="0912345678",
        )

        # 創建測試角色
        self.role = Role.objects.create(
            name="test_role", code="test_role", description="Test Role"
        )

        # 創建測試權限
        self.permission = Permission.objects.create(
            name="test_permission",
            code="test_permission",
            description="Test Permission",
        )

        # 建立角色權限關聯
        self.role.permissions.add(self.permission)

        # 將角色分配給用戶
        self.user.roles.add(self.role)

    def test_get_direct_permissions(self):
        """測試獲取使用者的直接權限"""
        # 分配直接權限
        self.user.permissions.add(self.permission)

        # 檢查直接權限
        direct_permissions = self.repository.get_direct_permissions(self.user.id)
        self.assertEqual(len(direct_permissions), 1)
        self.assertEqual(direct_permissions[0].id, self.permission.id)

    def test_get_role_permissions(self):
        """測試獲取使用者透過角色獲得的權限"""
        # 執行測試
        role_permissions = self.repository.get_role_permissions(self.user.id)

        # 驗證結果
        self.assertEqual(len(role_permissions), 1)
        self.assertEqual(role_permissions[0].id, self.permission.id)

    def test_get_all_permissions(self):
        """測試獲取使用者的所有權限（包括角色權限）"""
        # 分配直接權限
        self.user.permissions.add(self.permission)

        # 執行測試
        all_permissions = self.repository.get_all_permissions(self.user.id)

        # 驗證結果
        self.assertEqual(len(all_permissions), 1)
        self.assertEqual(all_permissions[0].id, self.permission.id)

    def test_get_roles(self):
        """測試獲取使用者的角色"""
        # 檢查角色
        roles = self.repository.get_roles(self.user.id)
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0].id, self.role.id)

    def test_has_permission(self):
        """測試檢查使用者是否擁有指定權限"""
        # 執行測試
        has_permission = self.repository.has_permission(
            self.user,
            api_url=self.permission.api_url,
            method=self.permission.method,
        )

        # 驗證結果
        self.assertTrue(has_permission)

    def test_has_any_permission(self):
        """測試檢查使用者是否擁有任一指定權限"""
        # 執行測試
        has_permission = self.repository.has_any_permission(
            self.user.id, [self.permission.id]
        )

        # 驗證結果
        self.assertTrue(has_permission)

    def test_has_all_permissions(self):
        """測試檢查使用者是否擁有所有指定權限"""
        # 執行測試
        has_permissions = self.repository.has_all_permissions(
            self.user.id, [self.permission.id]
        )

        # 驗證結果
        self.assertTrue(has_permissions)

    def test_add_direct_permission(self):
        """測試添加單個直接權限給使用者"""
        self.repository.add_direct_permission(self.user.id, self.permission.id)
        direct_permissions = self.repository.get_direct_permissions(self.user.id)
        self.assertIn(self.permission.id, {p.id for p in direct_permissions})

    def test_remove_direct_permission(self):
        """測試移除使用者的直接權限"""
        # 先添加權限
        self.repository.add_direct_permission(self.user.id, self.permission.id)

        # 再移除權限
        self.repository.remove_direct_permission(self.user.id, self.permission.id)
        direct_permissions = self.repository.get_direct_permissions(self.user.id)
        self.assertNotIn(self.permission.id, {p.id for p in direct_permissions})

    def test_remove_all_direct_permissions(self):
        """測試移除使用者的所有直接權限"""
        # 先添加權限
        self.repository.add_direct_permission(self.user.id, self.permission.id)

        # 移除所有權限
        self.repository.remove_all_direct_permissions(self.user.id)
        direct_permissions = self.repository.get_direct_permissions(self.user.id)
        self.assertEqual(len(direct_permissions), 0)

    def test_add_role(self):
        """測試添加單個角色給使用者"""
        # 創建新角色
        new_role = Role.objects.create(
            code="new_role", name="New Role", category="test", level=1
        )

        self.repository.add_role(self.user.id, new_role.id)
        roles = self.repository.get_roles(self.user.id)
        self.assertIn(new_role.id, {r.id for r in roles})

    def test_remove_role(self):
        """測試移除使用者的角色"""
        # 先添加新角色
        new_role = Role.objects.create(
            code="new_role", name="New Role", category="test", level=1
        )
        self.repository.add_role(self.user.id, new_role.id)

        # 再移除角色
        self.repository.remove_role(self.user.id, new_role.id)
        roles = self.repository.get_roles(self.user.id)
        self.assertNotIn(new_role.id, {r.id for r in roles})

    def test_remove_all_roles(self):
        """測試移除使用者的所有角色"""
        # 先添加新角色
        new_role = Role.objects.create(
            code="new_role", name="New Role", category="test", level=1
        )
        self.repository.add_role(self.user.id, new_role.id)

        # 移除所有角色
        self.repository.remove_all_roles(self.user.id)
        roles = self.repository.get_roles(self.user.id)
        self.assertEqual(len(roles), 0)
