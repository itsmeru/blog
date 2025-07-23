from django.contrib.auth import get_user_model
from django.test import TestCase

from ..repository import UserRepository

User = get_user_model()


class UserRepositoryTest(TestCase):
    def setUp(self):
        """測試前準備"""
        self.repo = UserRepository()
        self.test_data = {
            "email": "test@example.com",
            "phone": "0912345678",
            "nickname": "test_user",
            "password": "test_password",
        }
        self.user = User.objects.create_user(**self.test_data)

    def test_create_user(self):
        """測試建立使用者"""
        # Arrange
        new_user_data = {
            "email": "new@example.com",
            "phone": "0987654321",
            "nickname": "new_user",
            "password": "new_password",
        }

        # Act
        user = self.repo.create_user(**new_user_data)

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, new_user_data["email"])
        self.assertEqual(user.phone, new_user_data["phone"])
        self.assertEqual(user.nickname, new_user_data["nickname"])
        self.assertTrue(user.check_password(new_user_data["password"]))
        self.assertTrue(user.is_active)

    def test_get_by_email(self):
        """測試透過 email 取得使用者"""
        # Arrange
        expected_email = self.test_data["email"]

        # Act
        user = self.repo.get_by_email(expected_email)

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.email, expected_email)

    def test_get_by_phone(self):
        """測試透過電話取得使用者"""
        # Arrange
        expected_phone = self.test_data["phone"]

        # Act
        user = self.repo.get_by_phone(expected_phone)

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.phone, expected_phone)

    def test_get_by_account(self):
        """測試透過帳號（email 或 phone）取得使用者"""
        # Arrange
        expected_id = self.user.id

        # Act - 測試用 email 取得
        user1 = self.repo.get_by_account(self.test_data["email"])
        # Act - 測試用 phone 取得
        user2 = self.repo.get_by_account(self.test_data["phone"])

        # Assert
        self.assertEqual(user1.id, expected_id)
        self.assertEqual(user2.id, expected_id)

    def test_get_by_account_with_inactive_user(self):
        """測試透過帳號取得非活躍使用者"""
        # Arrange
        self.user.is_active = False
        self.user.save()

        # Act
        user1 = self.repo.get_by_account(self.test_data["email"])
        user2 = self.repo.get_by_account(self.test_data["phone"])

        # Assert
        self.assertIsNotNone(user1)
        self.assertIsNotNone(user2)
        self.assertFalse(user1.is_active)
        self.assertFalse(user2.is_active)
        self.assertEqual(user1.id, self.user.id)
        self.assertEqual(user2.id, self.user.id)

    def test_update_password(self):
        """測試更新密碼"""
        # Arrange
        new_password = "new_password123"

        # Act
        user = self.repo.update_password(self.user, new_password)

        # Assert
        self.assertTrue(user.check_password(new_password))
        self.assertFalse(user.check_password(self.test_data["password"]))

    def test_get_active_users(self):
        """測試取得活躍使用者"""
        # Arrange
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            phone="0911111111",
            nickname="inactive",
            password="password",
            is_active=False,
        )

        # Act
        active_users = self.repo.get_active_users()

        # Assert
        self.assertEqual(active_users.count(), 1)
        self.assertIn(self.user, active_users)
        self.assertNotIn(inactive_user, active_users)

    def test_deactivate_and_activate_user(self):
        """測試停用和啟用使用者"""
        # Act - 測試停用
        deactivated_user = self.repo.deactivate_user(self.user)
        active_users_after_deactivate = self.repo.get_active_users()

        # Assert - 停用後的狀態
        self.assertFalse(deactivated_user.is_active)
        self.assertEqual(active_users_after_deactivate.count(), 0)

        # Act - 測試啟用
        activated_user = self.repo.activate_user(deactivated_user)
        active_users_after_activate = self.repo.get_active_users()

        # Assert - 啟用後的狀態
        self.assertTrue(activated_user.is_active)
        self.assertEqual(active_users_after_activate.count(), 1)
        self.assertIn(activated_user, active_users_after_activate)
