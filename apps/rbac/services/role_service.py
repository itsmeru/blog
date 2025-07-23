from rest_framework.exceptions import NotFound, ValidationError
from apps.users.models import User
from apps.rbac.repositories import RoleRepository, UserRepository


class RoleService:
    repository_class = RoleRepository

    @classmethod
    def list_roles(cls):
        return cls.repository_class.get_active()

    @classmethod
    def create_role(cls, data, permissions):
        role = cls.repository_class.create(**data)
        if permissions:
            cls.repository_class.set_role_permissions(role.id, permissions)
        return role

    @classmethod
    def get_role(cls, pk):
        return cls.repository_class.get_by_id(pk)

    @classmethod
    def update_role(cls, pk, data, permissions):
        role = cls.repository_class.get_by_id(pk)
        cls.repository_class.update(role, **data)
        if permissions is not None:
            cls.repository_class.set_role_permissions(role.id, permissions)
        return role

    @classmethod
    def delete_role(cls, pk):
        role = cls.repository_class.get_by_id(pk)
        return cls.repository_class.delete(role)

    @classmethod
    def get_role_users(cls, role_id):
        role = cls.repository_class.get_by_id(role_id)
        return UserRepository.get_users_by_role(role)

    @classmethod
    def list_all_role_users(cls):
        return UserRepository.get_active_users()

    @staticmethod
    def set_role_users(role_id, user_ids):
        try:
            role = RoleRepository.get_by_id(role_id)
        except RoleRepository.model_class.DoesNotExist:
            raise NotFound("角色不存在")
        valid_user_ids = [
            uid for uid in user_ids if User.objects.filter(id=uid).exists()
        ]
        if len(valid_user_ids) != len(user_ids):
            raise ValidationError(
                {"invalid_ids": list(set(user_ids) - set(valid_user_ids))}
            )
        role.users.set(valid_user_ids)
        return role
