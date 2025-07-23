from django.contrib.auth import get_user_model
from django.test import TestCase

from ...services.user_permission_service import UserPermissionService
from ..seeders import RBACSeeder

User = get_user_model()


class UserPermissionServiceTest(TestCase):
    """使用者權限服務測試"""

    def setUp(self):
        """測試前準備"""
        self.service = UserPermissionService()
        self.seed_data = RBACSeeder.seed_all()
        self.user = self.seed_data["users"][0]
        self.role = self.seed_data["roles"][0]
        self.permission = self.seed_data["permissions"][0]

    def test_get_direct_permissions(self):
        """測試獲取使用者的直接權限"""
        # 分配直接權限
        self.service.assign_direct_permissions(self.user.id, [self.permission.id])

        # 檢查直接權限
        direct_permissions = self.service.get_direct_permissions(self.user.id)
        self.assertEqual(len(direct_permissions), 1)
        self.assertEqual(direct_permissions[0].id, self.permission.id)

    def test_get_role_permissions(self):
        """測試獲取使用者透過角色獲得的權限"""
        # 分配角色和權限
        self.service.assign_roles(self.user.id, [self.role.id])
        self.role.permissions.add(self.permission)

        # 檢查角色權限
        role_permissions = self.service.get_role_permissions(self.user.id)
        self.assertEqual(len(role_permissions), 1)
        self.assertEqual(role_permissions[0].id, self.permission.id)

    def test_get_all_permissions(self):
        """測試獲取使用者的所有權限（包括角色權限）"""
        # 分配直接權限和角色權限
        direct_permission = self.seed_data["permissions"][0]
        role_permission = self.seed_data["permissions"][1]

        self.service.assign_direct_permissions(self.user.id, [direct_permission.id])
        self.service.assign_roles(self.user.id, [self.role.id])
        self.role.permissions.add(role_permission)

        # 檢查所有權限
        all_permissions = self.service.get_all_permissions(self.user.id)
        self.assertEqual(len(all_permissions), 2)
        permission_ids = {p.id for p in all_permissions}
        self.assertIn(direct_permission.id, permission_ids)
        self.assertIn(role_permission.id, permission_ids)

    def test_get_roles(self):
        """測試獲取使用者的角色"""
        # 分配角色
        self.service.assign_roles(self.user.id, [self.role.id])

        # 檢查角色
        roles = self.service.get_roles(self.user.id)
        self.assertEqual(len(roles), 1)
        self.assertEqual(roles[0].id, self.role.id)

    def test_has_permission(self):
        """測試檢查使用者是否擁有指定權限"""
        # 分配直接權限
        self.service.assign_direct_permissions(self.user.id, [self.permission.id])

        # 檢查權限
        has_permission = self.service.has_permission(self.user.id, self.permission.code)
        self.assertTrue(has_permission)

        # 檢查不存在的權限
        has_permission = self.service.has_permission(self.user.id, "non_existent")
        self.assertFalse(has_permission)

    def test_has_any_permission(self):
        """測試檢查使用者是否擁有任一指定權限"""
        # 分配直接權限
        self.service.assign_direct_permissions(self.user.id, [self.permission.id])

        # 檢查權限
        has_permission = self.service.has_any_permission(
            self.user.id, [self.permission.code, "non_existent"]
        )
        self.assertTrue(has_permission)

        # 檢查不存在的權限
        has_permission = self.service.has_any_permission(
            self.user.id, ["non_existent1", "non_existent2"]
        )
        self.assertFalse(has_permission)

    def test_has_all_permissions(self):
        """測試檢查使用者是否擁有所有指定權限"""
        # 分配直接權限
        permission1 = self.seed_data["permissions"][0]
        permission2 = self.seed_data["permissions"][1]
        self.service.assign_direct_permissions(
            self.user.id, [permission1.id, permission2.id]
        )

        # 檢查權限
        has_permissions = self.service.has_all_permissions(
            self.user.id, [permission1.code, permission2.code]
        )
        self.assertTrue(has_permissions)

        # 檢查部分不存在的權限
        has_permissions = self.service.has_all_permissions(
            self.user.id, [permission1.code, "non_existent"]
        )
        self.assertFalse(has_permissions)

    def test_assign_direct_permissions(self):
        """測試分配直接權限給使用者"""
        permission_ids = [p.id for p in self.seed_data["permissions"][:2]]
        self.service.assign_direct_permissions(self.user.id, permission_ids)

        # 檢查權限是否正確分配
        direct_permissions = self.service.get_direct_permissions(self.user.id)
        self.assertEqual(len(direct_permissions), 2)
        self.assertEqual({p.id for p in direct_permissions}, set(permission_ids))

        # 測試分配給不存在的使用者
        with self.assertRaises(ValueError):
            self.service.assign_direct_permissions(999, permission_ids)

    def test_add_direct_permission(self):
        """測試添加單個直接權限給使用者"""
        self.service.add_direct_permission(self.user.id, self.permission.id)
        direct_permissions = self.service.get_direct_permissions(self.user.id)
        self.assertIn(self.permission.id, {p.id for p in direct_permissions})

    def test_remove_direct_permission(self):
        """測試移除使用者的直接權限"""
        # 先添加權限
        self.service.add_direct_permission(self.user.id, self.permission.id)

        # 再移除權限
        self.service.remove_direct_permission(self.user.id, self.permission.id)
        direct_permissions = self.service.get_direct_permissions(self.user.id)
        self.assertNotIn(self.permission.id, {p.id for p in direct_permissions})

    def test_remove_all_direct_permissions(self):
        """測試移除使用者的所有直接權限"""
        # 先添加多個權限
        permission_ids = [p.id for p in self.seed_data["permissions"][:2]]
        self.service.assign_direct_permissions(self.user.id, permission_ids)

        # 移除所有權限
        self.service.remove_all_direct_permissions(self.user.id)
        direct_permissions = self.service.get_direct_permissions(self.user.id)
        self.assertEqual(len(direct_permissions), 0)

    def test_assign_roles(self):
        """測試分配角色給使用者"""
        role_ids = [r.id for r in self.seed_data["roles"][:2]]
        self.service.assign_roles(self.user.id, role_ids)

        # 檢查角色是否正確分配
        roles = self.service.get_roles(self.user.id)
        self.assertEqual(len(roles), 2)
        self.assertEqual({r.id for r in roles}, set(role_ids))

        # 測試分配給不存在的使用者
        with self.assertRaises(ValueError):
            self.service.assign_roles(999, role_ids)

    def test_add_role(self):
        """測試添加單個角色給使用者"""
        self.service.add_role(self.user.id, self.role.id)
        roles = self.service.get_roles(self.user.id)
        self.assertIn(self.role.id, {r.id for r in roles})

    def test_remove_role(self):
        """測試移除使用者的角色"""
        # 先添加角色
        self.service.add_role(self.user.id, self.role.id)

        # 再移除角色
        self.service.remove_role(self.user.id, self.role.id)
        roles = self.service.get_roles(self.user.id)
        self.assertNotIn(self.role.id, {r.id for r in roles})

    def test_remove_all_roles(self):
        """測試移除使用者的所有角色"""
        # 先添加多個角色
        role_ids = [r.id for r in self.seed_data["roles"][:2]]
        self.service.assign_roles(self.user.id, role_ids)

        # 移除所有角色
        self.service.remove_all_roles(self.user.id)
        roles = self.service.get_roles(self.user.id)
        self.assertEqual(len(roles), 0)
