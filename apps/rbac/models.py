from django.db import models
from django.utils.translation import gettext_lazy as _

from core.mixins.choices import StageChoicesMixin


class Permission(models.Model, StageChoicesMixin):
    """權限模型"""

    code = models.CharField(_("權限代碼"), max_length=50, unique=True)
    name = models.CharField(_("權限名稱"), max_length=100)
    category = models.CharField(_("分類"), max_length=50)
    module = models.CharField(_("模組"), max_length=50)
    action = models.CharField(_("操作"), max_length=50)
    resource = models.CharField(_("資源"), max_length=50)
    level = models.IntegerField(_("層級"), default=1)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name=_("父權限"),
        related_name="children",
        null=True,
        blank=True,
    )
    description = models.TextField(_("描述"), blank=True, null=True)
    is_active = models.BooleanField(_("是否啟用"), default=True)
    stage = models.CharField(
        _("前台/後台"),
        max_length=20,
        choices=StageChoicesMixin.STAGE_CHOICES,
        default="backstage",
    )
    created_at = models.DateTimeField(_("建立時間"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新時間"), auto_now=True)
    api_url = models.CharField(_("API URL"), max_length=200, blank=True, null=True)
    method = models.CharField(_("HTTP 方法"), max_length=10, blank=True, null=True)
    function_zh = models.CharField(
        _("功能中文名稱"), max_length=100, blank=True, null=True
    )
    sort_order = models.IntegerField(_("排序"), default=0)

    class Meta:
        verbose_name = _("權限")
        verbose_name_plural = _("權限")
        ordering = ["module", "level", "code"]
        unique_together = ["module", "action", "resource"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Role(models.Model, StageChoicesMixin):
    """角色模型"""

    code = models.CharField(_("角色代碼"), max_length=50, unique=True)
    name = models.CharField(_("角色英文名稱"), max_length=100)
    name_zh = models.CharField(_("角色中文名稱"), max_length=100)
    description = models.TextField(_("描述"), blank=True, null=True)
    category = models.CharField(_("分類"), max_length=50)
    level = models.IntegerField(_("層級"), default=1)
    is_active = models.BooleanField(_("是否啟用"), default=True)
    stage = models.CharField(
        _("前台/後台"),
        max_length=20,
        choices=StageChoicesMixin.STAGE_CHOICES,
        default="backstage",
    )
    special_conditions = models.CharField(
        _("特殊條件"), max_length=200, blank=True, null=True
    )
    created_at = models.DateTimeField(_("建立時間"), auto_now_add=True)
    updated_at = models.DateTimeField(_("更新時間"), auto_now=True)
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        verbose_name=_("權限"),
        related_name="roles",
    )

    class Meta:
        verbose_name = _("角色")
        verbose_name_plural = _("角色")
        ordering = ["category", "level", "code"]

    def __str__(self):
        return f"{self.name_zh} ({self.code})"


class RolePermission(models.Model):
    """角色權限關聯模型"""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name=_("角色"),
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name=_("權限"),
        related_name="role_permissions",
    )
    is_active = models.BooleanField(_("是否啟用"), default=True)
    created_at = models.DateTimeField(_("建立時間"), auto_now_add=True)

    class Meta:
        verbose_name = _("角色權限")
        verbose_name_plural = _("角色權限")
        unique_together = ["role", "permission"]
        ordering = ["role", "permission"]

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class RoleHierarchy(models.Model):
    """角色階層關係模型"""

    parent_role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name=_("父角色"),
        related_name="children",
    )
    child_role = models.ForeignKey(
        Role, on_delete=models.CASCADE, verbose_name=_("子角色"), related_name="parents"
    )
    created_at = models.DateTimeField(_("建立時間"), auto_now_add=True)

    class Meta:
        verbose_name = _("角色階層")
        verbose_name_plural = _("角色階層")
        unique_together = ["parent_role", "child_role"]
        ordering = ["parent_role", "child_role"]

    def __str__(self):
        return f"{self.parent_role.name} -> {self.child_role.name}"
