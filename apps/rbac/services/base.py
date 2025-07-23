from typing import List, Optional, Type, TypeVar

from django.db import transaction
from django.db.models import Model

T = TypeVar("T", bound=Model)


class BaseService:
    """RBAC 服務層基礎類別"""

    def __init__(self, model_class: Type[T]):
        self.model_class = model_class

    @transaction.atomic
    def create(self, **kwargs) -> T:
        """建立新記錄"""
        return self.model_class.objects.create(**kwargs)

    @transaction.atomic
    def update(self, instance: T, **kwargs) -> T:
        """更新記錄"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    @transaction.atomic
    def delete(self, instance: T) -> None:
        """刪除記錄"""
        instance.delete()

    def get_by_id(self, id: int) -> Optional[T]:
        """根據 ID 獲取記錄"""
        return self.model_class.objects.filter(id=id).first()

    def get_all(self) -> List[T]:
        """獲取所有記錄"""
        return list(self.model_class.objects.all())

    def get_active(self) -> List[T]:
        """獲取所有啟用的記錄"""
        return list(self.model_class.objects.filter(is_active=True))
