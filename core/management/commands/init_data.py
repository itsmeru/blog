# yourapp/management/commands/seed_data.py
from django.core.management.base import BaseCommand

from apps.rbac.models import Permission, Role
from apps.users.models import User
from core.management.commands.seeds.bind_permissions import bind_permissions
from core.management.commands.seeds.set_permissions import set_permissions
from core.management.commands.seeds.set_roles import set_roles


def create_permissions():
    for permission_data in set_permissions():
        permission_dict = permission_data.__dict__
        Permission.objects.update_or_create(
            code=permission_dict["code"], defaults=permission_dict
        )


def create_roles():
    for role_data in set_roles():
        role_dict = role_data.__dict__
        Role.objects.update_or_create(code=role_dict["code"], defaults=role_dict)


def create_superuser(email, password):
    if User.objects.filter(email=email).exists():
        return False

    user = User.objects.create_superuser(
        email=email,
        password=password,
    )
    user.save()
    return True


class Command(BaseCommand):
    help = "Seed initial data"

    def handle(self, **kwargs):
        create_permissions()
        create_roles()
        bind_permissions()
