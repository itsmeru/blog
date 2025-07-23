from unittest.mock import patch

from django.test import TestCase

from apps.rbac.models import Permission
from apps.rbac.repositories import PermissionRepository
from apps.rbac.tests.seeders import RBACSeeder


class PermissionRepositoryTest(TestCase):
    """權限資料存取層測試"""

    def setUp(self):
        """測試前準備"""
        self.repository = PermissionRepository()
        self.test_data = RBACSeeder.get_test_data()
        self.permission = self.test_data["permissions"][0]
        self.permission_data = {
            "id": self.permission.id,
            "code": self.permission.code,
            "name": self.permission.name,
            "category": self.permission.category,
            "module": self.permission.module,
            "action": self.permission.action,
            "resource": self.permission.resource,
            "api_url": self.permission.api_url,
            "method": self.permission.method,
            "is_active": self.permission.is_active,
            "level": self.permission.level,
        }

    @patch("apps.rbac.repositories.PermissionRepository.get_by_code")
    def test_get_by_code(self, mock_get_by_code):
        """測試根據代碼獲取權限"""
        # 設定 mock 返回值
        mock_get_by_code.return_value = self.permission

        # 執行測試
        result = self.repository.get_by_code(self.permission_data["code"])

        # 驗證結果
        self.assertEqual(result.id, self.permission_data["id"])
        self.assertEqual(result.code, self.permission_data["code"])

        # 驗證 mock 被正確呼叫
        mock_get_by_code.assert_called_once_with(self.permission_data["code"])

    @patch("apps.rbac.repositories.PermissionRepository.get_by_codes")
    def test_get_by_codes(self, mock_get_by_codes):
        """測試根據多個代碼獲取權限"""
        # 準備測試資料
        codes = [p.code for p in self.test_data["permissions"][:2]]
        permissions = self.test_data["permissions"][:2]

        # 設定 mock 返回值
        mock_get_by_codes.return_value = permissions

        # 執行測試
        result = self.repository.get_by_codes(codes)

        # 驗證結果
        self.assertEqual(len(result), 2)
        self.assertEqual({p.code for p in result}, set(codes))

        # 驗證 mock 被正確呼叫
        mock_get_by_codes.assert_called_once_with(codes)

    @patch("apps.rbac.repositories.PermissionRepository.get_by_category")
    def test_get_by_category(self, mock_get_by_category):
        """測試根據分類獲取權限"""
        # 準備測試資料
        category = self.permission_data["category"]
        permissions = [
            p for p in self.test_data["permissions"] if p.category == category
        ]

        # 設定 mock 返回值
        mock_get_by_category.return_value = permissions

        # 執行測試
        result = self.repository.get_by_category(category)

        # 驗證結果
        self.assertTrue(all(p.category == category for p in result))

        # 驗證 mock 被正確呼叫
        mock_get_by_category.assert_called_once_with(category)

    @patch("apps.rbac.repositories.PermissionRepository.get_by_module")
    def test_get_by_module(self, mock_get_by_module):
        """測試根據模組獲取權限"""
        # 準備測試資料
        module = self.permission_data["module"]
        permissions = [p for p in self.test_data["permissions"] if p.module == module]

        # 設定 mock 返回值
        mock_get_by_module.return_value = permissions

        # 執行測試
        result = self.repository.get_by_module(module)

        # 驗證結果
        self.assertTrue(all(p.module == module for p in result))

        # 驗證 mock 被正確呼叫
        mock_get_by_module.assert_called_once_with(module)

    @patch("apps.rbac.repositories.PermissionRepository.get_by_action")
    def test_get_by_action(self, mock_get_by_action):
        """測試根據操作獲取權限"""
        # 準備測試資料
        action = self.permission_data["action"]
        permissions = [p for p in self.test_data["permissions"] if p.action == action]

        # 設定 mock 返回值
        mock_get_by_action.return_value = permissions

        # 執行測試
        result = self.repository.get_by_action(action)

        # 驗證結果
        self.assertTrue(all(p.action == action for p in result))

        # 驗證 mock 被正確呼叫
        mock_get_by_action.assert_called_once_with(action)

    @patch("apps.rbac.repositories.PermissionRepository.get_by_resource")
    def test_get_by_resource(self, mock_get_by_resource):
        """測試根據資源獲取權限"""
        # 準備測試資料
        resource = self.permission_data["resource"]
        permissions = [
            p for p in self.test_data["permissions"] if p.resource == resource
        ]

        # 設定 mock 返回值
        mock_get_by_resource.return_value = permissions

        # 執行測試
        result = self.repository.get_by_resource(resource)

        # 驗證結果
        self.assertTrue(all(p.resource == resource for p in result))

        # 驗證 mock 被正確呼叫
        mock_get_by_resource.assert_called_once_with(resource)

    @patch("apps.rbac.repositories.PermissionRepository.get_by_level")
    def test_get_by_level(self, mock_get_by_level):
        """測試根據層級獲取權限"""
        # 準備測試資料
        level = self.permission_data["level"]
        permissions = [p for p in self.test_data["permissions"] if p.level == level]

        # 設定 mock 返回值
        mock_get_by_level.return_value = permissions

        # 執行測試
        result = self.repository.get_by_level(level)

        # 驗證結果
        self.assertTrue(all(p.level == level for p in result))

        # 驗證 mock 被正確呼叫
        mock_get_by_level.assert_called_once_with(level)

    @patch("apps.rbac.repositories.PermissionRepository.get_by_parent")
    def test_get_by_parent(self, mock_get_by_parent):
        """測試根據父權限獲取子權限"""
        # 準備測試資料
        parent = Permission.objects.create(
            id=1000,
            code="test_parent",
            name="Test Parent",
            category="test",
            module="test",
            action="read",
            resource="parent",
        )
        child = Permission.objects.create(
            id=1001,
            code="test_child",
            name="Test Child",
            category="test",
            module="test",
            action="read",
            resource="child",
            parent_id=parent.id,
        )

        # 設定 mock 返回值
        mock_get_by_parent.return_value = [child]

        # 執行測試
        result = self.repository.get_by_parent(parent.id)

        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, child.id)

        # 驗證 mock 被正確呼叫
        mock_get_by_parent.assert_called_once_with(parent.id)

    @patch("apps.rbac.repositories.PermissionRepository.get_children")
    def test_get_children(self, mock_get_children):
        """測試獲取子權限"""
        # 準備測試資料
        parent = Permission.objects.create(
            id=1002,
            code="test_parent",
            name="Test Parent",
            category="test",
            module="test",
            action="read",
            resource="parent",
        )
        child = Permission.objects.create(
            id=1003,
            code="test_child",
            name="Test Child",
            category="test",
            module="test",
            action="read",
            resource="child",
            parent_id=parent.id,
        )

        # 設定 mock 返回值
        mock_get_children.return_value = [child]

        # 執行測試
        result = self.repository.get_children(parent.id)

        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, child.id)

        # 驗證 mock 被正確呼叫
        mock_get_children.assert_called_once_with(parent.id)

    @patch("apps.rbac.repositories.PermissionRepository.get_descendants")
    def test_get_descendants(self, mock_get_descendants):
        """測試獲取所有後代權限"""
        # 準備測試資料
        parent = Permission.objects.create(
            id=1004,
            code="test_parent",
            name="Test Parent",
            category="test",
            module="test",
            action="read",
            resource="parent",
        )
        child = Permission.objects.create(
            id=1005,
            code="test_child",
            name="Test Child",
            category="test",
            module="test",
            action="read",
            resource="child",
            parent_id=parent.id,
        )
        grandchild = Permission.objects.create(
            id=1006,
            code="test_grandchild",
            name="Test Grandchild",
            category="test",
            module="test",
            action="read",
            resource="grandchild",
            parent_id=child.id,
        )

        # 設定 mock 返回值
        mock_get_descendants.return_value = [child, grandchild]

        # 執行測試
        result = self.repository.get_descendants(parent.id)

        # 驗證結果
        self.assertEqual(len(result), 2)
        descendant_ids = {p.id for p in result}
        self.assertIn(child.id, descendant_ids)
        self.assertIn(grandchild.id, descendant_ids)

        # 驗證 mock 被正確呼叫
        mock_get_descendants.assert_called_once_with(parent.id)

    @patch("apps.rbac.repositories.PermissionRepository.get_ancestors")
    def test_get_ancestors(self, mock_get_ancestors):
        """測試獲取所有祖先權限"""
        # 準備測試資料
        parent = Permission.objects.create(
            id=1007,
            code="test_parent",
            name="Test Parent",
            category="test",
            module="test",
            action="read",
            resource="parent",
        )
        child = Permission.objects.create(
            id=1008,
            code="test_child",
            name="Test Child",
            category="test",
            module="test",
            action="read",
            resource="child",
            parent_id=parent.id,
        )
        grandchild = Permission.objects.create(
            id=1009,
            code="test_grandchild",
            name="Test Grandchild",
            category="test",
            module="test",
            action="read",
            resource="grandchild",
            parent_id=child.id,
        )

        # 設定 mock 返回值
        mock_get_ancestors.return_value = [parent, child]

        # 執行測試
        result = self.repository.get_ancestors(grandchild.id)

        # 驗證結果
        self.assertEqual(len(result), 2)
        ancestor_ids = {p.id for p in result}
        self.assertIn(parent.id, ancestor_ids)
        self.assertIn(child.id, ancestor_ids)

        # 驗證 mock 被正確呼叫
        mock_get_ancestors.assert_called_once_with(grandchild.id)

    @patch("apps.rbac.repositories.PermissionRepository.get_tree")
    def test_get_tree(self, mock_get_tree):
        """測試獲取權限樹"""
        # 準備測試資料
        parent = Permission.objects.create(
            id=1010,
            code="test_parent",
            name="Test Parent",
            category="test",
            module="test",
            action="read",
            resource="parent",
        )
        child = Permission.objects.create(
            id=1011,
            code="test_child",
            name="Test Child",
            category="test",
            module="test",
            action="read",
            resource="child",
            parent_id=parent.id,
        )
        grandchild = Permission.objects.create(
            id=1012,
            code="test_grandchild",
            name="Test Grandchild",
            category="test",
            module="test",
            action="read",
            resource="grandchild",
            parent_id=child.id,
        )

        # 設定 mock 返回值
        mock_get_tree.return_value = [parent, child, grandchild]

        # 執行測試
        result = self.repository.get_tree()

        # 驗證結果
        self.assertIn(parent, result)
        self.assertIn(child, result)
        self.assertIn(grandchild, result)

        # 驗證 mock 被正確呼叫
        mock_get_tree.assert_called_once_with()
