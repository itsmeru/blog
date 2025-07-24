from apps.rbac.repositories import PermissionRepository
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError


class PermissionService:
    repository_class = PermissionRepository

    @classmethod
    def list_permissions(cls):
        return cls.repository_class.get_active()

    @classmethod
    def create_permission(cls, data):
        return cls.repository_class.create(**data)

    @classmethod
    def get_permission(cls, pk):
        return cls.repository_class.get_by_id(pk)

    @classmethod
    def update_permission(cls, pk, data):
        permission = cls.repository_class.get_by_id(pk)
        try:
            return cls.repository_class.update(permission, **data)
        except IntegrityError as e:
            raise ValidationError({"code": ["權限代碼已存在，請使用其他 code。"]})

    @classmethod
    def delete_permission(cls, pk):
        permission = cls.repository_class.get_by_id(pk)
        return cls.repository_class.delete(permission)

    @classmethod
    def batch_update_permissions(cls, ids, is_active):
        return cls.repository_class.batch_update_permissions(ids, is_active)
