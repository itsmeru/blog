from django.db import models


class Permission(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    function_zh = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    action = models.CharField(max_length=50)
    resource = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    api_url = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Role(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)
    name_zh = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
    )

    def __str__(self):
        return f"{self.name} ({self.code})"


class RolePermission(models.Model):
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="role_permissions"
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="role_permissions"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("role", "permission")
        ordering = ["role", "permission"]

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"
