from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class UserAPITestCase(TestCase):
    def setUp(self):
        patcher = patch(
            "apps.rbac.permissions.IsRBACAllowed.has_permission", return_value=True
        )
        self.mock_permission = patcher.start()
        self.addCleanup(patcher.stop)

    def test_register_login_me(self):
        """正常流程：註冊、登入、查詢個人資料（/me/）皆成功"""
        # Arrange
        register_url = reverse("user-register")
        register_data = {
            "email": "test@example.com",
            "password": "yourpassword",
            "nickname": "測試用戶",
        }
        # Act
        response = self.client.post(
            register_url, register_data, content_type="application/json"
        )
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["data"]["email"], "test@example.com")

        # Arrange
        login_url = reverse("user-login")
        login_data = {"account": "test@example.com", "password": "yourpassword"}
        # Act
        response = self.client.post(
            login_url, login_data, content_type="application/json"
        )
        # Assert
        self.assertEqual(response.status_code, 200)
        access_token = response.json()["data"]["access"]

        # Arrange
        me_url = reverse("user-me")
        auth_header = f"Bearer {access_token}"
        # Act
        response = self.client.get(me_url, HTTP_AUTHORIZATION=auth_header)
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["email"], "test@example.com")

    def test_register_duplicate_email(self):
        """重複註冊相同 email，應回傳 400 並顯示 email 已存在"""
        # Arrange
        url = reverse("user-register")
        data = {"email": "dup@example.com", "password": "pw123", "nickname": "dup"}
        self.client.post(url, data, content_type="application/json")
        # Act
        response = self.client.post(url, data, content_type="application/json")
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Validation Error")
        self.assertIn("email", response.json()["errors"])
        self.assertEqual(response.json()["errors"]["email"], ["Email already exists"])

    def test_register_missing_fields(self):
        """註冊時缺少必要欄位（email、password、nickname），應回傳 400"""
        url = reverse("user-register")
        # Arrange - 缺 email
        data = {"password": "pw123", "nickname": "noemail"}
        # Act
        response = self.client.post(url, data, content_type="application/json")
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json()["errors"])
        # Arrange - 缺 password
        data = {"email": "no_pw@example.com", "nickname": "nopw"}
        # Act
        response = self.client.post(url, data, content_type="application/json")
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json()["errors"])
        # Arrange - 缺 nickname
        data = {"email": "no_nick@example.com", "password": "pw123"}
        # Act
        response = self.client.post(url, data, content_type="application/json")
        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertIn("nickname", response.json()["errors"])

    def test_login_wrong_password(self):
        """登入時密碼錯誤，應回傳 400 並顯示錯誤訊息"""
        # Arrange
        reg_url = reverse("user-register")
        self.client.post(
            reg_url,
            {"email": "pwtest@example.com", "password": "pw123", "nickname": "pwtest"},
            content_type="application/json",
        )
        login_url = reverse("user-login")
        data = {"account": "pwtest@example.com", "password": "wrongpw"}
        # Act
        response = self.client.post(login_url, data, content_type="application/json")
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json()["errors"])
        self.assertEqual(response.json()["errors"]["detail"], "Invalid credentials")

    def test_login_nonexistent_user(self):
        """登入不存在的帳號，應回傳 400 並顯示錯誤訊息"""
        # Arrange
        login_url = reverse("user-login")
        data = {"account": "notfound@example.com", "password": "pw123"}
        # Act
        response = self.client.post(login_url, data, content_type="application/json")
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json()["errors"])
        self.assertEqual(response.json()["errors"]["detail"], "Invalid credentials")

    def test_me_unauthorized(self):
        """未帶 JWT token 查詢 /me/，應回傳 401"""
        # Arrange
        me_url = reverse("user-me")
        # Act
        response = self.client.get(me_url)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.json()["errors"])
        self.assertEqual(
            response.json()["errors"]["detail"],
            "Authentication credentials were not provided.",
        )

    def test_login_inactive_user(self):
        """非活躍用戶嘗試登入，應回傳 400 並顯示用戶未啟用的訊息"""
        # Arrange - 註冊用戶
        reg_url = reverse("user-register")
        reg_data = {
            "email": "inactive@example.com",
            "password": "test123",
            "nickname": "inactive",
        }
        response = self.client.post(reg_url, reg_data, content_type="application/json")
        self.assertEqual(response.status_code, 201)

        # 停用用戶（直接修改資料庫）
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.get(email="inactive@example.com")
        user.is_active = False
        user.save()

        # Act - 嘗試登入
        login_url = reverse("user-login")
        login_data = {"account": "inactive@example.com", "password": "test123"}
        response = self.client.post(
            login_url, login_data, content_type="application/json"
        )

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertEqual(response_data["message"], "Authentication Failed")
        self.assertEqual(response_data["errors"]["detail"], "User is not active")
