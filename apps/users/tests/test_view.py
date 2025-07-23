from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class UserViewTest(TestCase):
    """用戶視圖測試"""

    def setUp(self):
        """測試前準備"""
        self.client = APIClient()
        self.register_url = reverse("user-register")
        self.login_url = reverse("user-login")
        self.refresh_url = reverse("user-refresh-token")
        self.forgot_password_url = reverse("user-forgot-password")
        self.me_url = reverse("user-me")
        self.department_list_url = reverse("department-list")

        # 創建測試用戶
        self.test_user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "nickname": "testnick",
            "phone": "0912345678",
        }
        self.test_user = User.objects.create_user(
            email=self.test_user_data["email"],
            password=self.test_user_data["password"],
            nickname=self.test_user_data["nickname"],
            phone=self.test_user_data["phone"],
        )

        patcher = patch(
            "apps.rbac.permissions.IsRBACAllowed.has_permission", return_value=True
        )
        self.mock_permission = patcher.start()
        self.addCleanup(patcher.stop)

    def test_register_success(self):
        """測試成功註冊"""
        # Arrange
        data = {
            "email": "new@example.com",
            "password": "newpassword123",
            "nickname": "newnick",
            "phone": "0987654321",
        }

        # Act
        response = self.client.post(self.register_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.json()["success"])
        self.assertIn("data", response.json())
        self.assertEqual(response.json()["data"]["email"], data["email"])
        self.assertEqual(response.json()["data"]["nickname"], data["nickname"])
        self.assertEqual(response.json()["data"]["phone"], data["phone"])

    def test_register_duplicate_email(self):
        """測試重複 email 註冊"""
        # Arrange
        data = {
            "email": self.test_user_data["email"],  # 使用已存在的 email
            "password": "newpassword123",
            "nickname": "newnick",
            "phone": "0987654321",
        }

        # Act
        response = self.client.post(self.register_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.json()["success"])
        self.assertIn("message", response.json())

    def test_login_success(self):
        """測試成功登入"""
        # Arrange
        data = {
            "account": self.test_user_data["email"],
            "password": self.test_user_data["password"],
        }

        # Act
        response = self.client.post(self.login_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["success"])
        self.assertIn("data", response.json())
        self.assertEqual(
            response.json()["data"]["nickname"], self.test_user_data["nickname"]
        )

    def test_login_wrong_password(self):
        """測試密碼錯誤"""
        # Arrange
        data = {"account": self.test_user_data["email"], "password": "wrongpassword"}

        # Act
        response = self.client.post(self.login_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.json()["success"])
        self.assertIn("message", response.json())

    def test_login_inactive_user(self):
        """測試未啟用用戶登入"""
        # Arrange
        self.test_user.is_active = False
        self.test_user.save()
        data = {
            "account": self.test_user_data["email"],
            "password": self.test_user_data["password"],
        }

        # Act
        response = self.client.post(self.login_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.json()["success"])
        self.assertIn("message", response.json())

    def test_forgot_password(self):
        """測試忘記密碼"""
        # Arrange
        data = {"account": self.test_user_data["email"]}

        # Act
        response = self.client.post(self.forgot_password_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["success"])
        self.assertIn("message", response.json())

    def test_forgot_password_nonexistent_user(self):
        """測試不存在用戶的忘記密碼請求"""
        # Arrange
        data = {"account": "nonexistent@example.com"}

        # Act
        response = self.client.post(self.forgot_password_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(response.json()["success"])
        self.assertIn("message", response.json())

    def test_me_authenticated(self):
        """測試已認證用戶獲取個人資料"""
        # Arrange
        self.client.force_authenticate(user=self.test_user)

        # Act
        response = self.client.get(self.me_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["success"])
        self.assertIn("data", response.json())
        self.assertEqual(response.json()["data"]["email"], self.test_user_data["email"])
        self.assertEqual(
            response.json()["data"]["nickname"], self.test_user_data["nickname"]
        )
        self.assertEqual(response.json()["data"]["phone"], self.test_user_data["phone"])

    def test_get_me_unauthenticated(self):
        """測試未認證用戶獲取個人信息"""
        url = reverse("user-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.json()["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_refresh_token_success(self):
        """測試成功刷新 token"""
        # Arrange - 先登入獲取 refresh token
        login_data = {
            "account": self.test_user_data["email"],
            "password": self.test_user_data["password"],
        }
        login_response = self.client.post(self.login_url, login_data, format="json")
        refresh_token = login_response.json()["data"]["refresh"]

        data = {"refresh": refresh_token}

        # Act
        response = self.client.post(self.refresh_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["success"])
        self.assertIn("data", response.json())
        self.assertIn("access", response.json()["data"])
        self.assertIn("refresh", response.json()["data"])

    def test_refresh_token_invalid_token(self):
        """測試無效 refresh token"""
        # Arrange
        data = {"refresh": "invalid_refresh_token"}

        # Act
        response = self.client.post(self.refresh_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.json()["success"])
        self.assertIn("message", response.json())

    def test_refresh_token_missing_token(self):
        """測試缺少 refresh token"""
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.refresh_url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.json()["success"])
        self.assertIn("message", response.json())

    def test_department_list_authenticated(self):
        """測試已認證用戶獲取部門列表"""
        # Arrange
        self.client.force_authenticate(user=self.test_user)

        # Act
        response = self.client.get(self.department_list_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["success"])
        self.assertIn("data", response.json())

        # 驗證返回的數據格式
        data = response.json()["data"]
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)

        # 驗證每個選項的格式
        for option in data:
            self.assertIn("label", option)
            self.assertIn("value", option)
            self.assertIsInstance(option["label"], str)
            self.assertIsInstance(option["value"], str)

        # 驗證預期的部門是否存在
        expected_departments = ["tech", "sales", "accounting", "operation"]
        actual_values = [option["label"] for option in data]
        for dept in expected_departments:
            self.assertIn(dept, actual_values)

    def test_department_list_unauthenticated(self):
        """測試未認證用戶獲取部門列表"""
        # Act
        response = self.client.get(self.department_list_url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
