from django.test import TestCase

from ...services.permission_service import PermissionService
from ..seeders import RBACSeeder


class PermissionServiceTest(TestCase):
    """權限服務測試"""

    def setUp(self):
        """測試前準備"""
        self.service = PermissionService()
        self.seed_data = RBACSeeder.seed_all()
        self.permission = self.seed_data["permissions"][0]

    def test_get_by_code(self):
        """測試根據代碼獲取權限"""
        permission = self.service.get_by_code(self.permission.code)
        self.assertEqual(permission.id, self.permission.id)
        self.assertEqual(permission.code, self.permission.code)

        # 測試不存在的代碼
        permission = self.service.get_by_code("non_existent")
        self.assertIsNone(permission)

    def test_get_by_codes(self):
        """測試根據多個代碼獲取權限"""
        codes = [p.code for p in self.seed_data["permissions"][:2]]
        permissions = self.service.get_by_codes(codes)
        self.assertEqual(len(permissions), 2)
        self.assertEqual({p.code for p in permissions}, set(codes))

    def test_get_by_category(self):
        """測試根據分類獲取權限"""
        category = self.permission.category
        permissions = self.service.get_by_category(category)
        self.assertTrue(all(p.category == category for p in permissions))

    def test_get_by_module(self):
        """測試根據模組獲取權限"""
        module = self.permission.module
        permissions = self.service.get_by_module(module)
        self.assertTrue(all(p.module == module for p in permissions))

    def test_get_by_action(self):
        """測試根據操作獲取權限"""
        action = self.permission.action
        permissions = self.service.get_by_action(action)
        self.assertTrue(all(p.action == action for p in permissions))

    def test_get_by_resource(self):
        """測試根據資源獲取權限"""
        resource = self.permission.resource
        permissions = self.service.get_by_resource(resource)
        self.assertTrue(all(p.resource == resource for p in permissions))

    def test_get_by_level(self):
        """測試根據層級獲取權限"""
        level = self.permission.level
        permissions = self.service.get_by_level(level)
        self.assertTrue(all(p.level == level for p in permissions))

    def test_create_with_parent(self):
        """測試建立帶有父權限的新權限"""
        parent = self.permission
        permission = self.service.create_with_parent(
            parent_id=parent.id,
            code="test_child",
            name="Test Child",
            category=parent.category,
            module=parent.module,
            action="read",
            resource="test",
        )
        self.assertEqual(permission.parent_id, parent.id)
        self.assertEqual(permission.code, "test_child")

        # 測試不存在的父權限
        with self.assertRaises(ValueError):
            self.service.create_with_parent(
                parent_id=999, code="test_invalid", name="Test Invalid"
            )

    def test_move_to_parent(self):
        """測試移動權限到新的父權限"""
        # 建立測試權限
        child = self.service.create(
            code="test_child",
            name="Test Child",
            category=self.permission.category,
            module=self.permission.module,
            action="read",
            resource="test",
        )

        # 移動到新父權限
        moved_permission = self.service.move_to_parent(child.id, self.permission.id)
        self.assertEqual(moved_permission.parent_id, self.permission.id)

        # 測試移動到不存在的父權限
        with self.assertRaises(ValueError):
            self.service.move_to_parent(child.id, 999)

        # 測試移動不存在的權限
        with self.assertRaises(ValueError):
            self.service.move_to_parent(999, self.permission.id)

        # 測試移動到自己的子權限（應該失敗）
        grandchild = self.service.create_with_parent(
            parent_id=child.id,
            code="test_grandchild",
            name="Test Grandchild",
            category=self.permission.category,
            module=self.permission.module,
            action="read",
            resource="test",
        )
        with self.assertRaises(ValueError):
            self.service.move_to_parent(self.permission.id, grandchild.id)

    def test_get_tree(self):
        """測試獲取權限樹"""
        # 建立一個簡單的權限樹
        parent = self.permission
        child = self.service.create_with_parent(
            parent_id=parent.id,
            code="test_child",
            name="Test Child",
            category=parent.category,
            module=parent.module,
            action="read",
            resource="test",
        )
        grandchild = self.service.create_with_parent(
            parent_id=child.id,
            code="test_grandchild",
            name="Test Grandchild",
            category=parent.category,
            module=parent.module,
            action="read",
            resource="test",
        )

        # 獲取整個樹
        tree = self.service.get_tree()
        self.assertIn(parent, tree)
        self.assertIn(child, tree)
        self.assertIn(grandchild, tree)

        # 獲取子樹
        subtree = self.service.get_tree(child.id)
        self.assertNotIn(parent, subtree)
        self.assertIn(child, subtree)
        self.assertIn(grandchild, subtree)
