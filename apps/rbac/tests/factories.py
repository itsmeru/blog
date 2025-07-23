import factory
from factory.django import DjangoModelFactory

from apps.rbac.models import Permission, Role, RoleHierarchy, RolePermission
from apps.users.models import User


class PermissionFactory(DjangoModelFactory):
    """權限工廠"""

    class Meta:
        model = Permission

    api_url = factory.Sequence(lambda n: f"/api/test{n}")
    method = "GET"
    function_zh = factory.Sequence(lambda n: f"測試功能{n}")
    module = "test"
    sort_order = 0
    is_active = True


class RoleFactory(DjangoModelFactory):
    """角色工廠"""

    class Meta:
        model = Role

    role_name = factory.Sequence(lambda n: f"test_role{n}")
    role_zh = factory.Sequence(lambda n: f"測試角色{n}")
    is_active = True


class RolePermissionFactory(DjangoModelFactory):
    """角色權限關聯工廠"""

    class Meta:
        model = RolePermission

    role = factory.SubFactory(RoleFactory)
    permission = factory.SubFactory(PermissionFactory)
    is_active = True


class RoleHierarchyFactory(DjangoModelFactory):
    """角色階層關係工廠"""

    class Meta:
        model = RoleHierarchy

    parent_role = factory.SubFactory(RoleFactory)
    child_role = factory.SubFactory(RoleFactory)


class UserFactory(DjangoModelFactory):
    """使用者工廠"""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"test{n}@example.com")
    nickname = factory.Sequence(lambda n: f"測試使用者{n}")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True
