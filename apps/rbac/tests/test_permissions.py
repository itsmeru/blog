import unittest
from collections import namedtuple
from unittest.mock import MagicMock, Mock, patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory

from apps.rbac.permissions import IsRBACAllowed

PermissionObj = namedtuple("PermissionObj", ["api_url", "method", "id"])


class DummyView:
    pass


class IsRBACAllowedTest(TestCase):
    def setUp(self):
        cache.clear()
        self.permission = IsRBACAllowed()
        self.factory = APIRequestFactory()
        self.user = Mock()
        self.user.is_authenticated = True
        self.user.is_superuser = False
        self.user.id = 1
        self.view = DummyView()

    def _get_request(self, path="/api/v1/resource", method="GET"):
        request = self.factory.generic(method, path)
        request.user = self.user
        return request

    @patch("apps.rbac.permissions.UserPermissionService.has_permission")
    def test_permission_granted(self, mock_has_permission):
        """測試權限檢查通過"""
        request = self._get_request()
        mock_has_permission.return_value = True

        allowed = self.permission.has_permission(request, self.view)

        self.assertTrue(allowed)
        mock_has_permission.assert_called_once_with(
            self.user, "/api/v1/resource", "GET"
        )

    @patch("apps.rbac.permissions.UserPermissionService.has_permission")
    def test_permission_denied(self, mock_has_permission):
        """測試權限檢查失敗"""
        request = self._get_request()
        mock_has_permission.side_effect = PermissionDenied("Access denied")

        with self.assertRaises(PermissionDenied):
            self.permission.has_permission(request, self.view)

        mock_has_permission.assert_called_once_with(
            self.user, "/api/v1/resource", "GET"
        )

    @override_settings(RBAC_WHITE_LIST=["/api/v1/white"])
    def test_white_list_bypass(self):
        """測試白名單路徑繞過權限檢查"""
        request = self._get_request(path="/api/v1/white")

        with patch(
            "apps.rbac.permissions.UserPermissionService.has_permission"
        ) as mock_has_permission:
            allowed = self.permission.has_permission(request, self.view)

            self.assertTrue(allowed)
            mock_has_permission.assert_not_called()

    def test_superuser_bypass(self):
        """測試超級管理員繞過權限檢查"""
        self.user.is_superuser = True
        request = self._get_request()

        with patch(
            "apps.rbac.permissions.UserPermissionService.has_permission"
        ) as mock_has_permission:
            allowed = self.permission.has_permission(request, self.view)

            self.assertTrue(allowed)
            mock_has_permission.assert_not_called()

    def test_anonymous_user_bypass(self):
        """測試匿名用戶繞過權限檢查"""
        self.user.is_authenticated = False
        request = self._get_request()

        with patch(
            "apps.rbac.permissions.UserPermissionService.has_permission"
        ) as mock_has_permission:
            allowed = self.permission.has_permission(request, self.view)

            self.assertTrue(allowed)
            mock_has_permission.assert_not_called()

    def test_non_api_path_bypass(self):
        """測試非API路徑繞過權限檢查"""
        request = self._get_request(path="/notapi/v1/resource")

        with patch(
            "apps.rbac.permissions.UserPermissionService.has_permission"
        ) as mock_has_permission:
            allowed = self.permission.has_permission(request, self.view)

            self.assertTrue(allowed)
            mock_has_permission.assert_not_called()

    def test_health_check_bypass(self):
        """測試健康檢查路徑繞過權限檢查"""
        health_paths = [
            "/api/v1/health",
            "/api/v1/health/",
            "/api/v1/health/liveness",
            "/api/v1/health/liveness/",
            "/api/v1/health/readiness",
            "/api/v1/health/readiness/",
        ]

        for path in health_paths:
            with self.subTest(path=path):
                request = self._get_request(path=path)

                with patch(
                    "apps.rbac.permissions.UserPermissionService.has_permission"
                ) as mock_has_permission:
                    allowed = self.permission.has_permission(request, self.view)

                    self.assertTrue(allowed)
                    mock_has_permission.assert_not_called()

    @override_settings(RBAC_WHITE_LIST=["/api/v1/white/", "/api/v1/public"])
    def test_white_list_with_trailing_slash_normalization(self):
        """測試白名單路徑的斜線正規化"""
        test_cases = [
            ("/api/v1/white", True),  # 白名單有斜線，請求沒有
            ("/api/v1/white/", True),  # 白名單有斜線，請求也有
            ("/api/v1/public", True),  # 白名單沒斜線，請求沒有
            ("/api/v1/public/", True),  # 白名單沒斜線，請求有
        ]

        for path, should_bypass in test_cases:
            with self.subTest(path=path):
                request = self._get_request(path=path)

                with patch(
                    "apps.rbac.permissions.UserPermissionService.has_permission"
                ) as mock_has_permission:
                    allowed = self.permission.has_permission(request, self.view)

                    self.assertTrue(allowed)
                    if should_bypass:
                        mock_has_permission.assert_not_called()

    @patch("apps.rbac.permissions.UserPermissionService.has_permission")
    def test_permission_service_exception_handling(self, mock_has_permission):
        """測試 UserPermissionService 異常處理"""
        request = self._get_request()
        mock_has_permission.side_effect = Exception("Service error")

        with self.assertRaises(Exception):
            self.permission.has_permission(request, self.view)

    def test_should_check_permission_logic(self):
        """測試 _should_check_permission 邏輯"""
        # 測試各種情況下是否需要檢查權限
        test_cases = [
            # (path, is_authenticated, is_superuser, expected)
            ("/api/v1/resource", True, False, True),  # 正常API請求
            ("/notapi/resource", True, False, False),  # 非API路徑
            ("/api/v1/resource", False, False, False),  # 匿名用戶
            ("/api/v1/resource", True, True, False),  # 超級管理員
            ("/api/v1/health", True, False, False),  # 健康檢查
            ("/api/v1/health/liveness", True, False, False),  # 健康檢查
            ("/api/v1/health/readiness", True, False, False),  # 健康檢查
        ]

        for path, is_authenticated, is_superuser, expected in test_cases:
            with self.subTest(
                path=path, is_authenticated=is_authenticated, is_superuser=is_superuser
            ):
                self.user.is_authenticated = is_authenticated
                self.user.is_superuser = is_superuser
                request = self._get_request(path=path)

                result = self.permission._should_check_permission(request)
                self.assertEqual(result, expected)
