from django.test import TestCase

from ...services.role_service import RoleService
from ..seeders import RBACSeeder


class RoleServiceTest(TestCase):
    """角色服務測試"""

    def setUp(self):
        """測試前準備"""
        self.service = RoleService()
        self.seed_data = RBACSeeder.seed_all()
        self.role = self.seed_data["roles"][0]
        self.permission = self.seed_data["permissions"][0]

    def test_get_by_code(self):
        """測試根據代碼獲取角色"""
        role = self.service.get_by_code(self.role.code)
        self.assertEqual(role.id, self.role.id)
        self.assertEqual(role.code, self.role.code)

        # 測試不存在的代碼
        role = self.service.get_by_code("non_existent")
        self.assertIsNone(role)

    def test_get_by_codes(self):
        """測試根據多個代碼獲取角色"""
        codes = [r.code for r in self.seed_data["roles"][:2]]
        roles = self.service.get_by_codes(codes)
        self.assertEqual(len(roles), 2)
        self.assertEqual({r.code for r in roles}, set(codes))

    def test_get_by_category(self):
        """測試根據分類獲取角色"""
        category = self.role.category
        roles = self.service.get_by_category(category)
        self.assertTrue(all(r.category == category for r in roles))

    def test_get_by_level(self):
        """測試根據層級獲取角色"""
        level = self.role.level
        roles = self.service.get_by_level(level)
        self.assertTrue(all(r.level == level for r in roles))

    def test_create_with_parent(self):
        """測試建立帶有父角色的新角色"""
        parent = self.role
        role = self.service.create_with_parent(
            parent_id=parent.id,
            code="test_child",
            name="Test Child",
            category=parent.category,
        )
        self.assertEqual(role.parent_id, parent.id)
        self.assertEqual(role.code, "test_child")

        # 測試不存在的父角色
        with self.assertRaises(ValueError):
            self.service.create_with_parent(
                parent_id=999, code="test_invalid", name="Test Invalid"
            )

    def test_move_to_parent(self):
        """測試移動角色到新的父角色"""
        # 建立測試角色
        child = self.service.create(
            code="test_child", name="Test Child", category=self.role.category
        )

        # 移動到新父角色
        moved_role = self.service.move_to_parent(child.id, self.role.id)
        self.assertEqual(moved_role.parent_id, self.role.id)

        # 測試移動到不存在的父角色
        with self.assertRaises(ValueError):
            self.service.move_to_parent(child.id, 999)

        # 測試移動不存在的角色
        with self.assertRaises(ValueError):
            self.service.move_to_parent(999, self.role.id)

        # 測試移動到自己的子角色（應該失敗）
        grandchild = self.service.create_with_parent(
            parent_id=child.id,
            code="test_grandchild",
            name="Test Grandchild",
            category=self.role.category,
        )
        with self.assertRaises(ValueError):
            self.service.move_to_parent(self.role.id, grandchild.id)

    def test_get_permissions(self):
        """測試獲取角色的權限"""
        permissions = self.service.get_permissions(self.role.id)
        self.assertEqual(len(permissions), len(self.seed_data["permissions"]))

    def test_get_inherited_permissions(self):
        """測試獲取角色繼承的權限"""
        # 建立父子角色關係
        child = self.service.create_with_parent(
            parent_id=self.role.id,
            code="test_child",
            name="Test Child",
            category=self.role.category,
        )

        # 父角色分配權限
        self.service.assign_permissions(self.role.id, [self.permission.id])

        # 檢查子角色是否繼承了父角色的權限
        inherited_permissions = self.service.get_inherited_permissions(child.id)
        self.assertEqual(len(inherited_permissions), 1)
        self.assertEqual(inherited_permissions[0].id, self.permission.id)

    def test_get_all_permissions(self):
        """測試獲取角色的所有權限（包括繼承的）"""
        # 建立父子角色關係
        child = self.service.create_with_parent(
            parent_id=self.role.id,
            code="test_child",
            name="Test Child",
            category=self.role.category,
        )

        # 父角色和子角色都分配權限
        parent_permission = self.seed_data["permissions"][0]
        child_permission = self.seed_data["permissions"][1]
        self.service.assign_permissions(self.role.id, [parent_permission.id])
        self.service.assign_permissions(child.id, [child_permission.id])

        # 檢查子角色的所有權限
        all_permissions = self.service.get_all_permissions(child.id)
        self.assertEqual(len(all_permissions), 2)
        permission_ids = {p.id for p in all_permissions}
        self.assertIn(parent_permission.id, permission_ids)
        self.assertIn(child_permission.id, permission_ids)

    def test_assign_permissions(self):
        """測試分配權限給角色"""
        permission_ids = [p.id for p in self.seed_data["permissions"][:2]]
        self.service.assign_permissions(self.role.id, permission_ids)

        # 檢查權限是否正確分配
        role_permissions = self.service.get_permissions(self.role.id)
        self.assertEqual(len(role_permissions), 2)
        self.assertEqual({p.id for p in role_permissions}, set(permission_ids))

        # 測試分配給不存在的角色
        with self.assertRaises(ValueError):
            self.service.assign_permissions(999, permission_ids)

    def test_add_permission(self):
        """測試添加單個權限給角色"""
        self.service.add_permission(self.role.id, self.permission.id)
        role_permissions = self.service.get_permissions(self.role.id)
        self.assertIn(self.permission.id, {p.id for p in role_permissions})

    def test_remove_permission(self):
        """測試移除角色的權限"""
        # 先添加權限
        self.service.add_permission(self.role.id, self.permission.id)

        # 再移除權限
        self.service.remove_permission(self.role.id, self.permission.id)
        role_permissions = self.service.get_permissions(self.role.id)
        self.assertNotIn(self.permission.id, {p.id for p in role_permissions})

    def test_remove_all_permissions(self):
        """測試移除角色的所有權限"""
        # 先添加多個權限
        permission_ids = [p.id for p in self.seed_data["permissions"][:2]]
        self.service.assign_permissions(self.role.id, permission_ids)

        # 移除所有權限
        self.service.remove_all_permissions(self.role.id)
        role_permissions = self.service.get_permissions(self.role.id)
        self.assertEqual(len(role_permissions), 0)
