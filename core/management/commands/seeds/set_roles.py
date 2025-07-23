from dataclasses import dataclass


@dataclass
class RoleField:
    code: str
    name: str
    name_zh: str
    description: str
    is_active: bool
    category: str


def set_roles():
    return [
        RoleField(
            code="admin",
            name="Administrator",
            name_zh="系統管理員",
            description="Full system access",
            is_active=True,
            category="system",
        ),
        RoleField(
            code="user",
            name="Regular User",
            name_zh="一般用戶",
            description="Basic user access",
            is_active=True,
            category="system",
        ),
    ]
