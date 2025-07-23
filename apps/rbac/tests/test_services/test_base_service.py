from django.db import models, transaction
from django.test import TestCase

from ...services.base import BaseService


# 建立測試用的模型
class TestModel(models.Model):
    """測試用模型"""

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = "rbac"


class TestBaseService(BaseService):
    """測試用服務"""

    def __init__(self):
        super().__init__(TestModel)


class BaseServiceTest(TestCase):
    """基礎服務測試"""

    def setUp(self):
        """測試前準備"""
        self.service = TestBaseService()
        # 建立測試資料
        self.test_obj1 = TestModel.objects.create(name="test1")
        self.test_obj2 = TestModel.objects.create(name="test2")
        self.test_obj3 = TestModel.objects.create(name="test3", is_active=False)

    def test_create(self):
        """測試建立記錄"""
        obj = self.service.create(name="test4")
        self.assertEqual(obj.name, "test4")
        self.assertTrue(obj.is_active)
        self.assertIsNotNone(obj.id)

    def test_update(self):
        """測試更新記錄"""
        updated_obj = self.service.update(self.test_obj1, name="updated")
        self.assertEqual(updated_obj.name, "updated")
        self.assertEqual(self.test_obj1.name, "updated")

    def test_delete(self):
        """測試刪除記錄"""
        obj_id = self.test_obj1.id
        self.service.delete(self.test_obj1)
        self.assertFalse(TestModel.objects.filter(id=obj_id).exists())

    def test_get_by_id(self):
        """測試根據 ID 獲取記錄"""
        obj = self.service.get_by_id(self.test_obj1.id)
        self.assertEqual(obj.id, self.test_obj1.id)
        self.assertEqual(obj.name, self.test_obj1.name)

        # 測試不存在的 ID
        obj = self.service.get_by_id(999)
        self.assertIsNone(obj)

    def test_get_all(self):
        """測試獲取所有記錄"""
        objects = self.service.get_all()
        self.assertEqual(len(objects), 3)
        self.assertIn(self.test_obj1, objects)
        self.assertIn(self.test_obj2, objects)
        self.assertIn(self.test_obj3, objects)

    def test_get_active(self):
        """測試獲取所有啟用的記錄"""
        active_objects = self.service.get_active()
        self.assertEqual(len(active_objects), 2)
        self.assertIn(self.test_obj1, active_objects)
        self.assertIn(self.test_obj2, active_objects)
        self.assertNotIn(self.test_obj3, active_objects)

    def test_transaction_rollback(self):
        """測試交易回滾"""
        try:
            with transaction.atomic():
                # 建立一個新記錄
                self.service.create(name="test5")
                # 故意觸發錯誤
                raise ValueError("Test error")
        except ValueError:
            pass

        # 確認新記錄沒有被建立
        self.assertFalse(TestModel.objects.filter(name="test5").exists())
