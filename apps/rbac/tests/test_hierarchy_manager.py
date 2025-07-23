import time
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase

from apps.rbac.hierarchy_manager import RoleHierarchyManager
from apps.rbac.models import Role, RoleHierarchy


class TestRoleHierarchyManager(TestCase):
    def setUp(self):
        cache.delete("role_hierarchy")
        # 建立角色
        self.r1 = Role.objects.create(code="r1", name="r1", name_zh="r1", category="A")
        self.r2 = Role.objects.create(code="r2", name="r2", name_zh="r2", category="A")
        self.r3 = Role.objects.create(code="r3", name="r3", name_zh="r3", category="A")
        self.r4 = Role.objects.create(code="r4", name="r4", name_zh="r4", category="A")
        self.r5 = Role.objects.create(code="r5", name="r5", name_zh="r5", category="A")
        # 建立階層
        RoleHierarchy.objects.create(parent_role=self.r1, child_role=self.r2)
        RoleHierarchy.objects.create(parent_role=self.r1, child_role=self.r3)
        RoleHierarchy.objects.create(parent_role=self.r2, child_role=self.r4)
        RoleHierarchy.objects.create(parent_role=self.r2, child_role=self.r5)

    def test_load(self):
        mgr = RoleHierarchyManager()
        result = mgr.load()
        # 轉成角色id
        expected = {
            self.r1.id: sorted(
                [self.r1.id, self.r2.id, self.r3.id, self.r4.id, self.r5.id]
            ),
            self.r2.id: sorted([self.r2.id, self.r4.id, self.r5.id]),
            self.r3.id: [self.r3.id],
            self.r4.id: [self.r4.id],
            self.r5.id: [self.r5.id],
        }
        for k, v in expected.items():
            self.assertEqual(sorted(result[k]), v)

    def test_cache(self):
        mgr = RoleHierarchyManager(cache_key="test_cache")
        cache.delete(mgr._cache_key)

        with (
            patch("apps.rbac.repositories.RoleRepository.get_all") as mock_get_all,
            patch(
                "apps.rbac.repositories.RoleHierarchyRepository.get_all_edges"
            ) as mock_get_edges,
        ):
            # 設定 mock 回傳值
            mock_get_all.return_value = Role.objects.all()
            mock_get_edges.return_value = [
                (self.r1.id, self.r2.id),
                (self.r1.id, self.r3.id),
                (self.r2.id, self.r4.id),
                (self.r2.id, self.r5.id),
            ]

            time.sleep(1)
            # 第一次 load 會寫入 cache
            mgr.load()
            self.assertIsNotNone(cache.get(mgr._cache_key))

            # 第二次 load 應該會使用 cache，不會重新查詢
            mock_get_all.reset_mock()
            mock_get_edges.reset_mock()
            mgr.load()
            mock_get_all.assert_not_called()
            mock_get_edges.assert_not_called()

    def test_reset(self):
        mgr = RoleHierarchyManager()
        mgr.load()
        self.assertIsNotNone(cache.get(mgr._cache_key))
        mgr.reset()
        self.assertIsNone(cache.get(mgr._cache_key))
