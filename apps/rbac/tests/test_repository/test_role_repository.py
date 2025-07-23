from django.test import TestCase

from apps.rbac.models import Permission, Role, RoleHierarchy, RolePermission
from apps.rbac.repositories import RoleRepository
from apps.rbac.tests.seeders import RBACSeeder


class RoleRepositoryTest(TestCase):
    """角色資料存取層測試"""

    def setUp(self):
        """測試前準備"""
        self.repository = RoleRepository()
        self.seed_data = RBACSeeder.seed_all()
        # 使用新創建的角色和權限，而不是使用已存在的
        self.role = Role.objects.create(
            code="test_role", name="Test Role", category="test", level=1
        )
        self.permission = Permission.objects.create(
            code="test_permission",
            name="Test Permission",
            category="test",
            module="test",
            action="test",
            resource="test",
        )

    def test_get_by_code(self):
        """測試根據代碼獲取角色"""
        role = self.repository.get_by_code(self.role.code)
        self.assertEqual(role.id, self.role.id)
        self.assertEqual(role.code, self.role.code)

        # 測試不存在的代碼
        role = self.repository.get_by_code("non_existent")
        self.assertIsNone(role)

    def test_get_by_codes(self):
        """測試根據多個代碼獲取角色"""
        codes = [r.code for r in self.seed_data["roles"][:2]]
        roles = self.repository.get_by_codes(codes)
        self.assertEqual(len(roles), 2)
        self.assertEqual({r.code for r in roles}, set(codes))

    def test_get_by_category(self):
        """測試根據分類獲取角色"""
        category = self.role.category
        roles = self.repository.get_by_category(category)
        self.assertTrue(all(r.category == category for r in roles))

    def test_get_by_level(self):
        """測試根據層級獲取角色"""
        level = self.role.level
        roles = self.repository.get_by_level(level)
        self.assertTrue(all(r.level == level for r in roles))

    def test_get_by_parent(self):
        """測試根據父角色獲取子角色"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)

        # 測試獲取子角色
        children = self.repository.get_by_parent(self.role.id)
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].id, child.id)

    def test_get_children(self):
        """測試獲取子角色"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)

        # 測試獲取子角色
        children = self.repository.get_children(self.role.id)
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].id, child.id)

    def test_get_descendants(self):
        """測試獲取所有後代角色"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        grandchild = Role.objects.create(
            code="test_grandchild",
            name="Test Grandchild",
            category=self.role.category,
            level=self.role.level + 2,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)
        RoleHierarchy.objects.create(parent_role=child, child_role=grandchild)

        # 測試獲取後代角色
        descendants = self.repository.get_descendants(self.role.id)
        self.assertEqual(len(descendants), 2)
        self.assertIn(child.id, [r.id for r in descendants])
        self.assertIn(grandchild.id, [r.id for r in descendants])

    def test_get_ancestors(self):
        """測試獲取所有祖先角色"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        grandchild = Role.objects.create(
            code="test_grandchild",
            name="Test Grandchild",
            category=self.role.category,
            level=self.role.level + 2,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)
        RoleHierarchy.objects.create(parent_role=child, child_role=grandchild)

        # 測試獲取祖先角色
        ancestors = self.repository.get_ancestors(grandchild.id)
        self.assertEqual(len(ancestors), 2)
        self.assertIn(self.role.id, [r.id for r in ancestors])
        self.assertIn(child.id, [r.id for r in ancestors])

    def test_get_tree(self):
        """測試獲取角色樹"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        grandchild = Role.objects.create(
            code="test_grandchild",
            name="Test Grandchild",
            category=self.role.category,
            level=self.role.level + 2,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)
        RoleHierarchy.objects.create(parent_role=child, child_role=grandchild)

        # 測試獲取角色樹
        tree = self.repository.get_tree(self.role.category)
        # 找到我們的測試角色樹
        test_tree = next((t for t in tree if t["id"] == self.role.id), None)
        self.assertIsNotNone(test_tree)
        self.assertEqual(len(test_tree["children"]), 1)
        self.assertEqual(test_tree["children"][0]["id"], child.id)
        self.assertEqual(len(test_tree["children"][0]["children"]), 1)
        self.assertEqual(test_tree["children"][0]["children"][0]["id"], grandchild.id)

    def test_get_permissions(self):
        """測試獲取角色的權限"""
        # 添加權限到角色
        RolePermission.objects.create(
            role=self.role, permission=self.permission, is_active=True
        )

        # 測試獲取權限
        permissions = self.repository.get_permissions(self.role.id)
        self.assertEqual(len(permissions), 1)
        self.assertEqual(permissions[0].id, self.permission.id)

    def test_get_inherited_permissions(self):
        """測試獲取角色繼承的權限"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)

        # 添加權限到父角色
        RolePermission.objects.create(
            role=self.role, permission=self.permission, is_active=True
        )

        # 測試獲取繼承的權限
        permissions = self.repository.get_inherited_permissions(child.id)
        self.assertEqual(len(permissions), 1)
        # 將 set 轉換為列表以便使用索引
        permissions_list = list(permissions)
        self.assertEqual(permissions_list[0].id, self.permission.id)

    def test_get_all_permissions(self):
        """測試獲取角色的所有權限（包括繼承的）"""
        # 建立父子關係
        child = Role.objects.create(
            code="test_child",
            name="Test Child",
            category=self.role.category,
            level=self.role.level + 1,
        )
        RoleHierarchy.objects.create(parent_role=self.role, child_role=child)

        # 添加權限到父角色和子角色
        RolePermission.objects.create(
            role=self.role, permission=self.permission, is_active=True
        )
        child_permission = Permission.objects.create(
            code="test_child_permission",
            name="Test Child Permission",
            category=self.permission.category,
            module=self.permission.module,
            action="test_child",
            resource="test_child",
        )
        RolePermission.objects.create(
            role=child, permission=child_permission, is_active=True
        )

        # 測試獲取所有權限
        permissions = self.repository.get_all_permissions(child.id)
        self.assertEqual(len(permissions), 2)
        self.assertIn(self.permission.id, [p.id for p in permissions])
        self.assertIn(child_permission.id, [p.id for p in permissions])
