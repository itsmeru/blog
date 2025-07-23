from apps.rbac.models import Permission, Role, RolePermission
from core.management.commands.seeds.set_permissions import set_permissions


def bind_permissions():
    try:
        admin_role = Role.objects.get(code="admin")
    except Role.DoesNotExist as e:
        print(f"Error: Required role not found: {e}")
        return

    all_permission_codes = [permission.code for permission in set_permissions()]

    for permission_code in all_permission_codes:
        try:
            permission = Permission.objects.get(code=permission_code)
            RolePermission.objects.update_or_create(
                role=admin_role, permission=permission, defaults={"is_active": True}
            )
        except Permission.DoesNotExist:
            print(f"Warning: Permission '{permission_code}' not found in database")

    return
