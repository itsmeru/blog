from django.core.management.base import BaseCommand
from rbac.models import Role, Permission, RolePermission
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # 建立角色
        editor, _ = Role.objects.get_or_create(name='Editor', defaults={'description': '編輯者'})
        admin, _ = Role.objects.get_or_create(name='Admin', defaults={'description': '管理員'})
        # 建立權限
        can_publish, _ = Permission.objects.get_or_create(code='can_publish', defaults={'description': '可發布'})
        can_delete, _ = Permission.objects.get_or_create(code='can_delete', defaults={'description': '可刪除'})
        # 角色分配權限
        RolePermission.objects.get_or_create(role=editor, permission=can_publish)
        RolePermission.objects.get_or_create(role=admin, permission=can_publish)
        RolePermission.objects.get_or_create(role=admin, permission=can_delete)
