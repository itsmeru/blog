from django.contrib.auth.hashers import check_password
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed, NotFound, ValidationError

from ..service import UserService


class UserServiceTest(TestCase):
    """UserService 測試類"""

    def setUp(self):
        """測試前置作業：創建測試用戶"""
        self.test_user = UserService.register_user(
            email="test@example.com",
            phone="1234567890",
            nickname="test_user",
            password="test_password",
        )

    def test_validate_email_unique(self):
        """測試郵箱唯一性驗證"""
        # Arrange
        duplicate_email = "test@example.com"

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            UserService._validate_email_unique(duplicate_email)
        self.assertIn("Email already exists", str(context.exception))

    def test_validate_user_exists(self):
        """測試用戶存在性驗證"""
        # Arrange - 使用不存在的用戶ID
        non_existent_id = 9999

        # Act & Assert
        with self.assertRaises(NotFound) as context:
            UserService._validate_user_exists(non_existent_id)
        self.assertIn("User not found", str(context.exception))

    def test_validate_user_active(self):
        """測試用戶活躍狀態驗證"""
        # Arrange - 停用用戶
        inactive_user = UserService.deactivate_user(self.test_user.id)

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            UserService._validate_user_active(inactive_user)
        self.assertIn("User is not active", str(context.exception))

    def test_register_user_success(self):
        """測試成功註冊用戶"""
        # Arrange
        email = "new@example.com"
        phone = "0987654321"
        nickname = "new_user"
        password = "new_password"

        # Act
        user = UserService.register_user(
            email=email, phone=phone, nickname=nickname, password=password
        )

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.phone, phone)
        self.assertEqual(user.nickname, nickname)
        self.assertTrue(check_password(password, user.password))
        self.assertTrue(user.is_active)

    def test_register_user_duplicate_email(self):
        """測試使用重複郵箱註冊"""
        # Arrange
        duplicate_email = "test@example.com"

        # Act & Assert
        with self.assertRaises(ValidationError) as context:
            UserService.register_user(
                email=duplicate_email,
                phone="9999999999",
                nickname="duplicate_user",
                password="password123",
            )
        self.assertIn("Email already exists", str(context.exception))

    def test_authenticate_success(self):
        """測試成功認證"""
        # Arrange
        account = "test@example.com"
        password = "test_password"

        # Act
        user = UserService.authenticate(account, password)

        # Assert
        self.assertIsNotNone(user)
        self.assertEqual(user.email, account)

    def test_authenticate_wrong_password(self):
        """測試密碼錯誤"""
        # Arrange
        account = "test@example.com"
        wrong_password = "wrong_password"

        # Act & Assert
        with self.assertRaises(AuthenticationFailed) as context:
            UserService.authenticate(account, wrong_password)
        self.assertIn("Invalid credentials", str(context.exception))

    def test_authenticate_inactive_user(self):
        """測試停用用戶認證"""
        # Arrange
        UserService.deactivate_user(self.test_user.id)
        account = "test@example.com"
        password = "test_password"

        # Act & Assert
        with self.assertRaises(AuthenticationFailed) as context:
            UserService.authenticate(account, password)
        self.assertIn("User is not active", str(context.exception))

    def test_start_forgot_password(self):
        """測試開始忘記密碼流程"""
        # Arrange
        account = "test@example.com"

        # Act
        UserService.start_forgot_password(account)

        # Assert - 目前只能確認不會拋出異常
        # TODO: 當實現完整的密碼重置流程後，添加更多斷言
        pass

    def test_start_forgot_password_invalid_account(self):
        """測試使用無效帳號開始忘記密碼流程"""
        # Arrange
        invalid_account = "nonexistent@example.com"

        # Act & Assert
        with self.assertRaises(NotFound) as context:
            UserService.start_forgot_password(invalid_account)
        self.assertIn("User not found", str(context.exception))

    def test_update_password(self):
        """測試更新密碼"""
        # Arrange
        new_password = "new_password123"

        # Act
        user = UserService.update_password(self.test_user.id, new_password)

        # Assert
        self.assertTrue(check_password(new_password, user.password))

    def test_get_active_users(self):
        """測試獲取活躍用戶"""
        # Arrange - 創建另一個活躍用戶
        UserService.register_user(
            email="active@example.com",
            phone="5555555555",
            nickname="active_user",
            password="password",
        )

        # Act
        active_users = UserService.get_active_users()

        # Assert
        self.assertEqual(active_users.count(), 2)
        self.assertTrue(all(user.is_active for user in active_users))

    def test_deactivate_and_activate_user(self):
        """測試停用和啟用用戶"""
        # Arrange
        user_id = self.test_user.id

        # Act - 停用
        deactivated_user = UserService.deactivate_user(user_id)

        # Assert
        self.assertFalse(deactivated_user.is_active)

        # Act - 啟用
        activated_user = UserService.activate_user(user_id)

        # Assert
        self.assertTrue(activated_user.is_active)

    def test_deactivate_nonexistent_user(self):
        """測試停用不存在的用戶"""
        # Arrange
        non_existent_id = 9999

        # Act & Assert
        with self.assertRaises(NotFound) as context:
            UserService.deactivate_user(non_existent_id)
        self.assertIn("User not found", str(context.exception))
