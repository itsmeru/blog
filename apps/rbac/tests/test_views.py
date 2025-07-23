from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.rbac.models import Permission, Role
from apps.rbac.tests.seeders import RBACSeeder
from apps.users.models import User


class PermissionViewSetTest(TestCase):
    """權限視圖集測試"""

    def setUp(self):
        """測試前準備"""
        self.client = APIClient()
        self.seed_data = RBACSeeder.seed_all()
        self.permission = self.seed_data["permissions"][0]

        # 創建測試用戶並設置權限
        self.test_user = User.objects.create_user(
            email="test@example.com", password="test123", nickname="Test User"
        )
        self.test_user.is_active = True
        self.test_user.enabled_permissions = [
            *[{"permission": p.id} for p in self.seed_data["permissions"]]
        ]
        self.test_user.save()

        # 認證用戶
        self.client.force_authenticate(user=self.test_user)

        self.patcher = patch(
            "apps.rbac.permissions.IsRBACAllowed.has_permission", return_value=True
        )
        self.mock_permission = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_list_permissions(self):
        """測試列出權限列表"""
        url = reverse("rbac:permission-list")
        response = self.client.get(url)
        data = response.json()["data"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the new grouped response format
        self.assertIn("groups", data)
        self.assertIn("total_permissions", data)
        self.assertIn("active_permissions", data)
        self.assertIsInstance(data["groups"], list)

    def test_list_permissions_with_stage_filter(self):
        """測試使用前台/後台過濾的權限列表"""
        # Create test permission with frontstage
        Permission.objects.create(
            code="test_frontstage",
            name="Test Frontstage Permission",
            category="test",
            module="test",
            action="test",
            resource="test",
            stage="frontstage",
            function_zh="前台測試權限",
        )

        url = reverse("rbac:permission-list")
        response = self.client.get(url, {"stage": "frontstage"})
        data = response.json()["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("groups", data)

        # Check that only frontstage permissions are returned
        for group in data["groups"]:
            for permission in group["permissions"]:
                # We need to check the actual permission object
                perm = Permission.objects.get(id=permission["id"])
                self.assertEqual(perm.stage, "frontstage")

    def test_list_permissions_with_active_filter(self):
        """測試使用啟用/禁用過濾的權限列表"""
        # Create inactive permission
        Permission.objects.create(
            code="test_inactive",
            name="Test Inactive Permission",
            category="test",
            module="test",
            action="test",
            resource="test",
            is_active=False,
            function_zh="測試禁用權限",
        )

        url = reverse("rbac:permission-list")
        response = self.client.get(url, {"is_active": "false"})
        data = response.json()["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that only inactive permissions are returned
        for group in data["groups"]:
            for permission in group["permissions"]:
                self.assertFalse(permission["is_active"])

    def test_list_permissions_with_search(self):
        """測試使用搜尋功能的權限列表"""
        # Create permission with specific function_zh
        Permission.objects.create(
            code="test_search",
            name="Test Search Permission",
            category="test",
            module="test",
            action="test",
            resource="test",
            function_zh="特殊搜尋功能",
        )

        url = reverse("rbac:permission-list")
        response = self.client.get(url, {"search": "特殊搜尋"})
        data = response.json()["data"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that search results contain the keyword
        found = False
        for group in data["groups"]:
            for permission in group["permissions"]:
                if "特殊搜尋" in permission["function_zh"]:
                    found = True
        self.assertTrue(found)

    def test_create_permission(self):
        """測試建立權限"""
        url = reverse("rbac:permission-list")
        data = {
            "code": "test_permission",
            "name": "Test Permission",
            "category": "test",
            "module": "test",
            "action": "test",
            "resource": "test",
            "level": 1,
            "stage": "backstage",  # Include the new required field
            "function_zh": "測試權限",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Permission.objects.count(), len(self.seed_data["permissions"]) + 1
        )

        # Verify the created permission has the correct stage
        created_permission = Permission.objects.get(code="test_permission")
        self.assertEqual(created_permission.stage, "backstage")

    def test_update_permission(self):
        """測試更新權限"""
        url = reverse("rbac:permission-detail", args=[self.permission.id])
        data = {"name": "Updated Permission"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.name, "Updated Permission")

    def test_update_permission_stage(self):
        """測試更新權限的前台/後台設定"""
        url = reverse("rbac:permission-detail", args=[self.permission.id])
        data = {"stage": "frontstage"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.permission.refresh_from_db()
        self.assertEqual(self.permission.stage, "frontstage")

    def test_delete_permission(self):
        """測試刪除權限"""
        url = reverse("rbac:permission-detail", args=[self.permission.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Permission.objects.count(), len(self.seed_data["permissions"]) - 1
        )


class PermissionBatchUpdateViewSetTest(TestCase):
    """權限批次更新視圖集測試"""

    def setUp(self):
        """測試前準備"""
        self.client = APIClient()
        self.seed_data = RBACSeeder.seed_all()

        # Create additional test permissions
        self.permission1 = Permission.objects.create(
            code="test_permission_1",
            name="Test Permission 1",
            category="test",
            module="test",
            action="test",
            resource="test1",
            is_active=True,
            function_zh="測試權限1",
        )
        self.permission2 = Permission.objects.create(
            code="test_permission_2",
            name="Test Permission 2",
            category="test",
            module="test",
            action="test",
            resource="test2",
            is_active=True,
            function_zh="測試權限2",
        )

        # 創建測試用戶並設置權限
        self.test_user = User.objects.create_user(
            email="test@example.com", password="test123", nickname="Test User"
        )
        self.test_user.is_active = True
        self.test_user.enabled_permissions = [
            *[{"permission": p.id} for p in self.seed_data["permissions"]]
        ]
        self.test_user.save()

        # 認證用戶
        self.client.force_authenticate(user=self.test_user)

        self.patcher = patch(
            "apps.rbac.permissions.IsRBACAllowed.has_permission", return_value=True
        )
        self.mock_permission = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_batch_update_permissions_activate(self):
        """測試批次啟用權限"""
        # First disable the permissions
        self.permission1.is_active = False
        self.permission2.is_active = False
        self.permission1.save()
        self.permission2.save()

        url = reverse("rbac:permission-batch-update")
        data = {
            "permission_ids": [self.permission1.id, self.permission2.id],
            "is_active": True,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(response_data["updated_count"], 2)
        self.assertIn("已更新 2 個權限", response_data["message"])

        # Verify permissions are now active
        self.permission1.refresh_from_db()
        self.permission2.refresh_from_db()
        self.assertTrue(self.permission1.is_active)
        self.assertTrue(self.permission2.is_active)

    def test_batch_update_permissions_deactivate(self):
        """測試批次禁用權限"""
        url = reverse("rbac:permission-batch-update")
        data = {
            "permission_ids": [self.permission1.id, self.permission2.id],
            "is_active": False,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()["data"]
        self.assertEqual(response_data["updated_count"], 2)

        # Verify permissions are now inactive
        self.permission1.refresh_from_db()
        self.permission2.refresh_from_db()
        self.assertFalse(self.permission1.is_active)
        self.assertFalse(self.permission2.is_active)

    def test_batch_update_permissions_invalid_ids(self):
        """測試批次更新不存在的權限ID"""
        url = reverse("rbac:permission-batch-update")
        data = {
            "permission_ids": [9999, 9998],  # Non-existent IDs
            "is_active": True,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_batch_update_permissions_mixed_ids(self):
        """測試批次更新混合存在和不存在的權限ID"""
        url = reverse("rbac:permission-batch-update")
        data = {
            "permission_ids": [self.permission1.id, 9999],  # One valid, one invalid
            "is_active": True,
        }
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_batch_update_permissions_empty_list(self):
        """測試批次更新空的權限ID列表"""
        url = reverse("rbac:permission-batch-update")
        data = {"permission_ids": [], "is_active": True}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()["data"]
        self.assertEqual(response_data["updated_count"], 0)


class RoleViewSetTest(TestCase):
    """角色視圖集測試"""

    def setUp(self):
        """測試前準備"""
        self.client = APIClient()
        self.seed_data = RBACSeeder.seed_all()
        self.role = self.seed_data["roles"][0]
        self.permission = self.seed_data["permissions"][0]

        # 創建測試用戶並設置權限
        self.test_user = User.objects.create_user(
            email="test@example.com", password="test123", nickname="Test User"
        )
        self.test_user.is_active = True

        # 創建設置角色權限的權限
        Permission.objects.create(
            code="set_role_permissions",
            name="Set Role Permissions",
            description="Can set role permissions",
            category="rbac",
            module="roles",
            action="set_permissions",
            resource="roles",
            api_url="/api/v1/rbac/roles/{id}/set-permissions/",
            method="POST",
            level=1,
            is_active=True,
            function_zh="Set Role Permissions",
        )

        # 設置用戶權限
        self.test_user.enabled_permissions = [
            p.id for p in self.seed_data["permissions"]
        ]
        self.test_user.save()

        # 認證用戶
        self.client.force_authenticate(user=self.test_user)

        self.patcher = patch(
            "apps.rbac.permissions.IsRBACAllowed.has_permission", return_value=True
        )
        self.mock_permission = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        super().tearDown()

    def test_list_roles(self):
        """測試列出角色列表"""
        url = reverse("rbac:role-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["data"]["roles"]), len(self.seed_data["roles"]))

    def test_create_role(self):
        """測試建立角色"""
        url = reverse("rbac:role-list")
        data = {
            "code": "test_role",
            "name": "Test Role",
            "name_zh": "測試角色",
            "description": "Test Role Description",
            "category": "test",
            "level": 1,
            "stage": "backstage",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Role.objects.count(), len(self.seed_data["roles"]) + 1)

    def test_update_role(self):
        """測試更新角色"""
        url = reverse("rbac:role-detail", args=[self.role.id])
        data = {
            "code": self.role.code,
            "name": "Updated Role",
            "name_zh": "測試角色",
            "category": self.role.category,
            "level": self.role.level,
            "stage": self.role.stage,
            "is_active": self.role.is_active,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.role.refresh_from_db()
        self.assertEqual(self.role.name_zh, "測試角色")

    def test_delete_role(self):
        """測試刪除角色"""
        url = reverse("rbac:role-detail", args=[self.role.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Role.objects.count(), len(self.seed_data["roles"]) - 1)
